"""AWTRIX NG audio library services. Isolated from working radio/MQTT entities."""
from __future__ import annotations
import re
from pathlib import Path
from urllib.parse import quote

from aiohttp import ClientError, ClientTimeout, FormData
import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_PREFIX

MP3_DIR = Path('/config/awtrix_ng_audio')
MP3_MAX_SIZE = 4 * 1024 * 1024


def get_api(hass, target):
    target = target.strip().lower()
    for entry in hass.config_entries.async_entries(DOMAIN):
        if target in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
            dev = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            if dev and dev.get('http'):
                return dev['http']
    raise HomeAssistantError('Dispositivo AWTRIX NG HTTP non disponibile: ' + target)


def valid_name(value, limit=32):
    if not isinstance(value, str) or len(value) > limit or not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise HomeAssistantError('Nome audio non valido (lettere, numeri, _ o -)')
    return value


async def upload_mp3(hass, api, filename):
    if not isinstance(filename, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,32}\.mp3', filename, flags=re.I):
        raise HomeAssistantError('Il nome deve essere Nome.mp3, senza cartelle')
    path = MP3_DIR / filename
    try:
        size = path.stat().st_size
        if size < 4 or size > MP3_MAX_SIZE:
            raise HomeAssistantError('File MP3 vuoto o oltre 4 MiB')
        # MP3 identification is performed by firmware, not by file extension.
        data = path.read_bytes()
    except OSError as exc:
        raise HomeAssistantError(f'File MP3 non trovato: {path}') from exc
    form = FormData()
    form.add_field('file', data, filename=filename, content_type='audio/mpeg')
    session = async_get_clientsession(hass)
    try:
        async with session.post(api.host + '/api/v1/audio/mp3', data=form, timeout=ClientTimeout(total=35)) as response:
            body = await response.text()
            if response.status >= 400:
                raise HomeAssistantError(f'AWTRIX upload: HTTP {response.status}: {body[:300]}')
            try:
                result = await response.json(content_type=None)
            except (ValueError, TypeError) as exc:
                raise HomeAssistantError('Risposta upload MP3 non valida') from exc
            if not isinstance(result, dict) or result.get('ok') is not True:
                raise HomeAssistantError(f'Upload MP3 non confermato: {result!r}')
            return result
    except (ClientError, TimeoutError) as exc:
        raise HomeAssistantError(f'AWTRIX upload MP3: {exc}') from exc


def register_audio_management_services(hass):
    target = {vol.Required('device'): cv.string}
    name_schema = {**target, vol.Required('name'): cv.string}

    async def audio_status(call):
        return await get_api(hass, call.data['device']).request('GET', '/api/v1/audio')

    async def melody_list(call):
        return await get_api(hass, call.data['device']).request('GET', '/api/v1/audio/melodies')

    async def melody_save(call):
        name = valid_name(call.data['name'], 24)
        rtttl = call.data['rtttl']
        if not rtttl.strip() or len(rtttl.encode('utf-8')) > 512:
            raise HomeAssistantError('Melodia RTTTL vuota o troppo lunga')
        return await get_api(hass, call.data['device']).request('PUT', f'/api/v1/audio/melodies/{quote(name, safe="")}', {'rtttl': rtttl})

    async def melody_delete(call):
        name = valid_name(call.data['name'], 24)
        return await get_api(hass, call.data['device']).request('DELETE', f'/api/v1/audio/melodies/{quote(name, safe="")}')

    async def mp3_list(call):
        return await get_api(hass, call.data['device']).request('GET', '/api/v1/audio/mp3')

    async def mp3_upload(call):
        return await upload_mp3(hass, get_api(hass, call.data['device']), call.data['filename'])

    async def mp3_delete(call):
        name = valid_name(call.data['name'])
        return await get_api(hass, call.data['device']).request('DELETE', f'/api/v1/audio/mp3/{quote(name, safe="")}')

    async def mp3_rename(call):
        old = valid_name(call.data['old_name'])
        new = valid_name(call.data['new_name'])
        return await get_api(hass, call.data['device']).request('POST', '/api/v1/audio/mp3/rename', {'from': old, 'to': new})

    async def audio_play(call):
        kinds = [k for k in ('file', 'rtttl', 'song', 'speech', 'station') if k in call.data]
        if len(kinds) != 1:
            raise HomeAssistantError('Scegliere una sola sorgente audio')
        key = kinds[0]
        data = {key: call.data[key]}
        if call.data.get('loop'):
            if key == 'station':
                raise HomeAssistantError('loop non è supportato per la radio')
            data['loop'] = True
        return await get_api(hass, call.data['device']).request('POST', '/api/v1/audio/play', data)

    async def audio_stop_group(call):
        return await get_api(hass, call.data['device']).request('POST', '/api/v1/audio/stop', {'group': call.data['group']})

    def register(name, handler, schema, response=SupportsResponse.OPTIONAL):
        hass.services.async_register(DOMAIN, name, handler, schema=vol.Schema(schema), supports_response=response)

    register('audio_status', audio_status, target, SupportsResponse.ONLY)
    register('melody_list', melody_list, target, SupportsResponse.ONLY)
    register('melody_save', melody_save, {**name_schema, vol.Required('rtttl'): cv.string})
    register('melody_delete', melody_delete, name_schema)
    register('mp3_list', mp3_list, target, SupportsResponse.ONLY)
    register('mp3_upload', mp3_upload, {**target, vol.Required('filename'): cv.string})
    register('mp3_delete', mp3_delete, name_schema)
    register('mp3_rename', mp3_rename, {**target, vol.Required('old_name'): cv.string, vol.Required('new_name'): cv.string})
    register('audio_play_source', audio_play, {**target, **{vol.Optional(k): cv.string for k in ('file', 'rtttl', 'song', 'speech', 'station')}, vol.Optional('loop', default=False): cv.boolean})
    register('audio_stop_group', audio_stop_group, {**target, vol.Required('group'): vol.In(['alert', 'app', 'radio'])})
