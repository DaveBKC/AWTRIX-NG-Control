"""Named and layout AWTRIX NG notifications via the documented HTTP API.

Isolated services: existing MQTT notifications, entities and radio are unchanged.
"""
from __future__ import annotations

import re
from urllib.parse import quote

import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_PREFIX

_NOTIFICATION_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


def validate_notification(payload: dict) -> dict:
    """Check common layout errors before submitting to device; it does final validation."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("La notifica deve contenere un oggetto JSON non vuoto")
    if 'layout' in payload:
        layout = payload['layout']
        if not isinstance(layout, dict) or layout.get('version') != 1:
            raise ValueError('Il layout deve avere version: 1')
        regions = layout.get('regions')
        if not isinstance(regions, list) or not 1 <= len(regions) <= 16:
            raise ValueError('Il layout richiede da 1 a 16 regioni')
        ids = set()
        for item in regions:
            if not isinstance(item, dict):
                raise ValueError('Ogni regione deve essere un oggetto JSON')
            rid = item.get('id')
            box = item.get('box')
            if not isinstance(rid, str) or not rid or rid in ids:
                raise ValueError('Ogni regione deve avere un id univoco')
            ids.add(rid)
            if not (isinstance(box, list) and len(box) == 4 and
                    all(type(v) is int for v in box) and
                    box[0] >= 0 and box[1] >= 0 and box[2] > 0 and box[3] > 0):
                raise ValueError(f'Regione {rid}: box deve essere [x,y,larghezza,altezza]')
        if any(k in payload for k in ('text', 'icon', 'draw', 'effect', 'scroll')):
            raise ValueError('Con layout, text/icon/draw/effect/scroll vanno dentro regions')
    if 'name' in payload and not _NOTIFICATION_NAME.fullmatch(str(payload['name'])):
        raise ValueError('Nome notifica: 1-64 caratteri tra lettere, cifre, _ e -')
    if 'durationMs' in payload and (type(payload['durationMs']) is not int or payload['durationMs'] < 0):
        raise ValueError('durationMs deve essere un intero >= 0')
    return payload


def register_advanced_notification_services(hass):
    target = {vol.Required('device'): cv.string}

    def get_api(device_name):
        target_name = device_name.strip().lower()
        for entry in hass.config_entries.async_entries(DOMAIN):
            if target_name in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
                dev = hass.data.get(DOMAIN, {}).get(entry.entry_id)
                if dev and dev.get('http'):
                    return dev['http']
        raise HomeAssistantError(f'Dispositivo AWTRIX NG HTTP non disponibile: {device_name}')

    async def send(call):
        try:
            payload = validate_notification(dict(call.data['data']))
        except (ValueError, TypeError) as exc:
            raise HomeAssistantError(str(exc)) from exc
        response = await get_api(call.data['device']).request('POST', '/api/v1/notifications', payload)
        return response if isinstance(response, dict) else {'ok': True}

    async def dismiss_named_http(call):
        name = call.data['name'].strip()
        if not _NOTIFICATION_NAME.fullmatch(name) or name == 'active':
            raise HomeAssistantError('Nome non valido oppure riservato: active')
        await get_api(call.data['device']).request('DELETE', '/api/v1/notifications/' + quote(name, safe=''))

    hass.services.async_register(DOMAIN, 'notification_advanced', send,
        schema=vol.Schema({**target, vol.Required('data'): dict}),
        supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(DOMAIN, 'notification_dismiss_named_http', dismiss_named_http,
        schema=vol.Schema({**target, vol.Required('name'): cv.string}))
