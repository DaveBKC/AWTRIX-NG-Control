"""TTS for AWTRIX NG Control: generate locally in HA, send MP3 via HTTP clip."""
from __future__ import annotations

import logging

from aiohttp import ClientError, ClientTimeout
import voluptuous as vol
from homeassistant.components import tts
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from urllib.parse import urlsplit

from .const import DOMAIN, CONF_PREFIX
from .native_targets import entry_for_device_id

_LOGGER = logging.getLogger(__name__)
MAX_CLIP = 2 * 1024 * 1024


def _resolve_http(hass: HomeAssistant, data: dict):
    """Resolve either an existing prefix/entry ID or HA device selector."""
    device_id = data.get("device_id")
    # HA's target selector may provide a list rather than a single ID.
    if isinstance(device_id, list):
        if len(device_id) != 1 or not isinstance(device_id[0], str):
            raise HomeAssistantError("Select exactly one AWTRIX device")
        device_id = device_id[0]
    name = data.get("device")
    if bool(device_id) == bool(name):
        raise HomeAssistantError("Specify exactly one of device_id or device")
    if device_id:
        entry = entry_for_device_id(hass, device_id)
    else:
        needle = name.strip().lower()
        entry = next((entry for entry in hass.config_entries.async_entries(DOMAIN)
                      if needle in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower())), None)
        if entry is None:
            raise HomeAssistantError(f"Unknown AWTRIX device: {name}")
    dev = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not dev or not dev.get("http") or not dev["http"].host:
        raise HomeAssistantError("AWTRIX NG HTTP address is not configured")
    return dev["http"]


async def _say(hass: HomeAssistant, data: dict) -> None:
    api = _resolve_http(hass, data)
    message = data["message"].strip()
    if not message:
        raise HomeAssistantError("TTS message is empty")
    # Home Assistant uses FFmpeg conversion when the TTS provider cannot emit MP3.
    options = dict(data.get("options") or {})
    options.update({"preferred_format": "mp3", "preferred_sample_channels": 1})
    media_id = tts.generate_media_source_id(
        hass, message=message, engine=data.get("engine") or None,
        language=data.get("language") or None, options=options,
        cache=data.get("cache", True),
    )
    extension, audio = await tts.async_get_media_source_audio(hass, media_id)
    if extension.lower().lstrip(".") != "mp3":
        raise HomeAssistantError(f"Expected MP3 from HA TTS, got {extension!r}")
    if not audio or len(audio) > MAX_CLIP:
        raise HomeAssistantError(
            f"TTS audio exceeds AWTRIX clip limit (2 MiB): {len(audio)} bytes"
        )
    address = str(api.host).strip().rstrip("/")
    if not address.startswith(("http://", "https://")):
        address = "http://" + address
    parsed = urlsplit(address)
    if not parsed.hostname or parsed.path not in ("", "/"):
        raise HomeAssistantError("Invalid AWTRIX HTTP address")
    session = async_get_clientsession(hass)
    try:
        async with session.post(
            address + "/api/v1/audio/clip",
            data=audio,
            headers={"Content-Type": "audio/mpeg"},
            timeout=ClientTimeout(total=35),
        ) as response:
            result = await response.text()
            if response.status >= 400:
                raise HomeAssistantError(
                    f"AWTRIX audio clip HTTP {response.status}: {result[:240]}"
                )
            _LOGGER.debug("AWTRIX TTS sent (%d bytes)", len(audio))
    except (ClientError, TimeoutError) as exc:
        raise HomeAssistantError(f"AWTRIX TTS connection failed: {exc}") from exc


def register_tts_services(hass: HomeAssistant) -> None:
    """Register independent TTS action without changing existing services."""
    schema = vol.Schema({
        vol.Optional("device"): cv.string,
        vol.Optional("device_id"): vol.Any(cv.string, [cv.string]),
        vol.Required("message"): vol.All(cv.string, vol.Length(min=1, max=2000)),
        vol.Optional("engine"): cv.string,
        vol.Optional("language"): cv.string,
        vol.Optional("options"): dict,
        vol.Optional("cache", default=True): cv.boolean,
    })

    async def handle(call):
        await _say(hass, call.data)

    hass.services.async_register(DOMAIN, "say", handle, schema=schema)
