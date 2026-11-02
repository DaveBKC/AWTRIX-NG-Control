"""Berry script management via AWTRIX NG HTTP API.

Separate from existing MQTT entities and services.  HTTP responses are
validated: a 200 status alone does not mean a Berry script compiled.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from aiohttp import ClientError, ClientTimeout
import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components import persistent_notification
from .const import DOMAIN, CONF_PREFIX

NAME = re.compile(r"[A-Za-z0-9_-]{1,32}\Z")
SCRIPT_DIR = Path("/config/awtrix_ng_scripts")
MAX_SOURCE_BYTES = 256 * 1024


def _name(value: str) -> str:
    if not NAME.fullmatch(value):
        raise HomeAssistantError("Nome script non valido: usare 1-32 caratteri alfanumerici, _ o -")
    return value


def _device(hass, target: str):
    target = target.strip().lower()
    for entry in hass.config_entries.async_entries(DOMAIN):
        if target in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
            dev = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            if dev and dev.get('http'):
                return dev
    raise HomeAssistantError(f"Dispositivo AWTRIX NG HTTP non disponibile: {target}")


async def _text_request(hass, api, method: str, path: str, source: str | None = None):
    """Raw script upload/download: firmware expects Berry text, not JSON."""
    session = async_get_clientsession(hass)
    options = {"timeout": ClientTimeout(total=20)}
    if source is not None:
        options['data'] = source.encode('utf-8')
        options['headers'] = {'Content-Type': 'text/plain; charset=utf-8'}
    try:
        async with session.request(method, api.host + path, **options) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise HomeAssistantError(f"AWTRIX {method} {path}: HTTP {resp.status}: {body[:350]}")
            if method == 'GET':
                return body
            try:
                return await _parse_json(body)
            except ValueError as exc:
                raise HomeAssistantError(f"Risposta script inattesa: {body[:250]}") from exc
    except (ClientError, TimeoutError) as exc:
        raise HomeAssistantError(f"AWTRIX HTTP: {exc}") from exc


async def _parse_json(body):
    import json
    return json.loads(body)


def _check_install(result):
    if not isinstance(result, dict) or result.get('ok') is not True:
        raise HomeAssistantError(f"Risposta installazione non valida: {result!r}")
    if result.get('error') is not None:
        raise HomeAssistantError(
            "Script salvato sul dispositivo ma NON eseguibile: " + str(result['error'])
        )
    return result


def _read_local(filename: str) -> str:
    # Filename only: no arbitrary access to HA secrets or other config files.
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}\.(?:ax|be|berry|txt)", filename, re.I):
        raise HomeAssistantError("File non valido: specificare solo nome.ax/.be/.berry/.txt")
    file = SCRIPT_DIR / filename
    try:
        raw = file.read_bytes()
    except OSError as exc:
        raise HomeAssistantError(f"File mancante in {SCRIPT_DIR}: {filename}") from exc
    if not raw or len(raw) > MAX_SOURCE_BYTES:
        raise HomeAssistantError("Sorgente Berry vuoto o superiore a 256 KiB")
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise HomeAssistantError("Lo script deve essere UTF-8") from exc


def register_script_services(hass):
    target = {vol.Required('device'): cv.string}

    async def list_scripts(call):
        api = _device(hass, call.data['device'])['http']
        result = await api.request('GET', '/api/v1/apps')
        if not isinstance(result, list):
            result = result.get('apps') if isinstance(result, dict) else None
        if not isinstance(result, list):
            # Existing firmware's GET /api/v1/ returns apps if /apps doesn't.
            result = await api.request('GET', '/api/v1/')
            if isinstance(result, dict):
                result = result.get('apps')
        if not isinstance(result, list):
            raise HomeAssistantError('API non ha restituito un elenco di applicazioni')
        scripts = [
            {'name': x['name'], 'enabled': x.get('enabled'), 'inLoop': x.get('inLoop'),
             'error': x.get('error'), 'meta': x.get('meta')}
            for x in result if isinstance(x, dict) and x.get('origin') == 'script' and isinstance(x.get('name'), str)
        ]
        return {'scripts': scripts, 'count': len(scripts)}

    async def read_script(call):
        api = _device(hass, call.data['device'])['http']
        name = _name(call.data['name'])
        source = await _text_request(hass, api, 'GET', f'/api/v1/apps/script/{quote(name, safe="")}')
        return {'name': name, 'source': source}

    async def install(call):
        api = _device(hass, call.data['device'])['http']
        name = _name(call.data['name'])
        source = _read_local(call.data['filename'])
        path = f'/api/v1/apps/script/{quote(name, safe="")}'
        # Never overwrite an installed script by accident; update separately.
        apps = await api.request('GET', '/api/v1/')
        if isinstance(apps, dict):
            apps = apps.get('apps', [])
        if not isinstance(apps, list):
            raise HomeAssistantError('Impossibile verificare gli script installati')
        if any(x.get('name') == name and x.get('present') for x in apps if isinstance(x, dict)):
            raise HomeAssistantError('Script già presente. Usa script_update per aggiornarlo in sicurezza')
        response = await _text_request(hass, api, 'PUT', path, source)
        _check_install(response)
        await api.refresh()
        return response

    async def update(call):
        api = _device(hass, call.data['device'])['http']
        name = _name(call.data['name'])
        source = _read_local(call.data['filename'])
        existing = await _text_request(hass, api, 'GET', f'/api/v1/apps/script/{quote(name, safe="")}')
        if source == existing:
            return {'ok': True, 'name': name, 'unchanged': True}
        capabilities = await api.request('GET', '/api/v1/capabilities')
        if not isinstance(capabilities, dict) or capabilities.get('scriptUpdates') is not True:
            raise HomeAssistantError('Firmware senza scriptUpdates: aggiornamento condizionale non supportato')
        response = await api.request('PUT', f'/api/v1/apps/script-update/{quote(name, safe="")}',
                                     {'expected_source': existing, 'source': source})
        _check_install(response)
        await api.refresh()
        return response

    async def remove(call):
        api = _device(hass, call.data['device'])['http']
        name = _name(call.data['name'])
        # Explicit destructive service; never remove other app origins.
        apps = await api.request('GET', '/api/v1/')
        if isinstance(apps, dict):
            apps = apps.get('apps', [])
        found = next((x for x in apps if isinstance(x, dict) and x.get('name') == name and x.get('present')), None) if isinstance(apps, list) else None
        if not found or found.get('origin') != 'script':
            raise HomeAssistantError('Rimozione rifiutata: il nome non identifica uno script Berry presente')
        await api.request('DELETE', f'/api/v1/apps/{quote(name, safe="")}')
        await api.refresh()

    async def config_get(call):
        api = _device(hass, call.data['device'])['http']
        name = _name(call.data['name'])
        result = await api.request('GET', f'/api/v1/apps/{quote(name, safe="")}/config')
        if not isinstance(result, dict):
            raise HomeAssistantError('Configurazione script non valida')
        return result

    async def config_set(call):
        api = _device(hass, call.data['device'])['http']
        name = _name(call.data['name'])
        fields = call.data['settings']
        if not fields:
            raise HomeAssistantError('Specificare almeno un parametro')
        return await api.request('PATCH', f'/api/v1/apps/{quote(name, safe="")}/config', fields)

    response_target = vol.Schema(target)
    named = {**target, vol.Required('name'): cv.string}
    hass.services.async_register(DOMAIN, 'script_list', list_scripts, schema=response_target,
                                 supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, 'script_read', read_script, schema=vol.Schema(named),
                                 supports_response=SupportsResponse.ONLY)
    for service, handler in [('script_install', install), ('script_update', update)]:
        hass.services.async_register(DOMAIN, service, handler,
            schema=vol.Schema({**named, vol.Required('filename'): cv.string}),
            supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, 'script_remove', remove, schema=vol.Schema(named))
    hass.services.async_register(DOMAIN, 'script_config_get', config_get,
        schema=vol.Schema(named), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, 'script_config_set', config_set,
        schema=vol.Schema({**named, vol.Required('settings'): dict}),
        supports_response=SupportsResponse.OPTIONAL)
