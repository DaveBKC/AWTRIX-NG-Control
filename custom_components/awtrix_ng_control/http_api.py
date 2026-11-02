"""HTTP reading and radio station controls for AWTRIX NG."""
from __future__ import annotations
import asyncio
from urllib.parse import quote
from aiohttp import ClientError, ClientTimeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging
from homeassistant.exceptions import HomeAssistantError
from datetime import timedelta
_LOGGER = logging.getLogger(__name__)

class AwtrixHttp:
    def __init__(self, hass, host, device):
        self.hass, self.host, self.device = hass, host.strip().rstrip('/'), device
        if not self.host.startswith(('http://','https://')):
            self.host = 'http://' + self.host
        if self.host.endswith('/api/v1'):
            self.host = self.host[:-7]
        self.station_names = []
        self.stations = []
        self.apps = []
        self.app_names = []
        self.capabilities = {}
        self.connected = False
        self.endpoint_ok = {"apps": False, "stations": False, "audio": False, "capabilities": False}
        self.endpoint_errors = {}
        self.coordinator = DataUpdateCoordinator(hass, _LOGGER, name="AWTRIX NG HTTP", update_method=self._async_update, update_interval=timedelta(seconds=30))
        self.audio = {}
        self.display_info = {}
        self.display_settings = {}
        self.screen = None
        self.remove_timer = None
        self.lock = asyncio.Lock()

    async def request(self, method, path, data=None):
        if not path.startswith('/api/v1/') or '://' in path or '..' in path:
            raise HomeAssistantError('Only local /api/v1/ paths are accepted')
        session = async_get_clientsession(self.hass)
        try:
            async with session.request(method, self.host + path, **({"json": data} if data is not None else {}), timeout=ClientTimeout(total=12)) as resp:
                resp.raise_for_status()
                if resp.content_type == 'application/json':
                    return await resp.json()
                return await resp.read()
        except (ClientError, TimeoutError, ValueError, TypeError) as exc:
            raise HomeAssistantError(f'AWTRIX HTTP {method} {path}: {exc}') from exc

    async def start(self):
        # First fetch finishes BEFORE Home Assistant creates select/image entities.
        self._remove_coordinator_listener = self.coordinator.async_add_listener(lambda: None)
        await self.coordinator.async_refresh()

    async def stop(self):
        if hasattr(self, "_remove_coordinator_listener"):
            self._remove_coordinator_listener()

    async def _async_update(self):
        await self.refresh()
        return {"endpoints": dict(self.endpoint_ok)}

    async def refresh(self):
        responses = 0
        for endpoint, target in [('/api/v1/audio/stations','stations'),('/api/v1/capabilities','capabilities'),('/api/v1/audio','audio'),('/api/v1/apps','apps')]:
            try:
                if target == 'apps':
                    # On this firmware the user's verified /api/v1/ endpoint
                    # returns a populated applications array. Prefer it; an
                    # empty but syntactically valid /apps result must not hide it.
                    failures = []
                    result = None
                    for path in ('/api/v1/', '/api/v1/apps'):
                        try:
                            candidate = await self.request('GET', path)
                            apps = candidate if isinstance(candidate, list) else (
                                candidate.get('apps') if isinstance(candidate, dict) else None
                            )
                            if not isinstance(apps, list) or not any(
                                isinstance(app, dict) and isinstance(app.get('name'), str)
                                for app in apps
                            ):
                                failures.append(f'{path}: no named applications')
                                continue
                            result = candidate
                            break
                        except (HomeAssistantError, ValueError, TypeError) as exc:
                            failures.append(f'{path}: {exc}')
                    if result is None:
                        raise ValueError('Applications unavailable: ' + '; '.join(failures))
                else:
                    result = await self.request('GET', endpoint)
                if target == 'stations' and not (isinstance(result, dict) and isinstance(result.get('stations'), list)):
                    raise ValueError('Risposta /audio/stations non valida: atteso oggetto stations')
                responses += 1
                self.endpoint_ok[target] = True
                self.endpoint_errors.pop(target, None)
                if target == 'stations':
                    self.stations = result.get('stations', []) if isinstance(result, dict) else []
                    self.station_names = [x.get('name') for x in self.stations if isinstance(x, dict) and x.get('name')]
                elif target == 'apps':
                    self.apps = result if isinstance(result, list) else result.get('apps', []) if isinstance(result, dict) else []
                    self.app_names = [item['name'] for item in self.apps if isinstance(item, dict) and item.get('name') and item.get('present', True) and item.get('enabled', False) and not item.get('headless', False)]
                else:
                    setattr(self, target, result)
            except Exception as exc:
                self.endpoint_ok[target] = False
                self.endpoint_errors[target] = str(exc)
                _LOGGER.exception('AWTRIX NG %s failed for %s: %s', endpoint, self.host, exc)
        # Additional display controls use their own endpoints.  Failures here
        # must never make the existing apps/radio selectors unavailable.
        for path, field in (('/api/v1/display', 'display_info'),
                            ('/api/v1/settings', 'display_settings')):
            try:
                result = await self.request('GET', path)
                if not isinstance(result, dict):
                    raise ValueError('Expected JSON object')
                setattr(self, field, result)
                self.endpoint_errors.pop(field, None)
            except Exception as exc:
                self.endpoint_errors[field] = str(exc)
                _LOGGER.warning('AWTRIX NG %s unavailable: %s', path, exc)
        self.connected = responses > 0
        if not self.connected:
            _LOGGER.error('AWTRIX NG cannot reach %s: %s', self.host, self.endpoint_errors)
        self.device['state']['http_error'] = '; '.join(f'{k}: {v}' for k,v in self.endpoint_errors.items()) if self.endpoint_errors else ''
        self.notify()

    def notify(self):
        for listener in tuple(self.device['listeners']): listener()

    async def modify_station(self, name, url):
        if not (1 <= len(name) <= 24): raise HomeAssistantError('Station name length must be 1-24')
        if url is not None and (not url.startswith(('http://','https://')) or len(url) > 255):
            raise HomeAssistantError('Invalid radio stream URL')
        async with self.lock:
            fresh = await self.request('GET', '/api/v1/audio/stations')
            old = fresh.get('stations', [])
            updated = [x for x in old if x.get('name') != name]
            if url is not None: updated.append({'name':name,'url':url})
            if len(updated)>32: raise HomeAssistantError('Maximum 32 stations')
            await self.request('PUT','/api/v1/audio/stations', {'stations':updated})
            await self.refresh()
