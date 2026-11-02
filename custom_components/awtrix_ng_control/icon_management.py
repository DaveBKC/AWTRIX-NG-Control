"""Icon asset operations for AWTRIX NG, independent from existing controls."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlencode

from aiohttp import ClientError, ClientTimeout, FormData
import voluptuous as vol
from homeassistant.components import mqtt  # noqa: F401 - integration dependency
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_PREFIX

_ICON = re.compile(r"^[A-Za-z0-9_-]{1,32}\.(?:gif|jpg|jpeg)$", re.I)


def _validate_name(name: str) -> str:
    if not _ICON.fullmatch(name):
        raise HomeAssistantError("Nome icona non valido: usare lettere, numeri, _ o -, estensione .gif/.jpg/.jpeg")
    return name


def _device_http(hass, device_name):
    for entry in hass.config_entries.async_entries(DOMAIN):
        if device_name.lower() in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
            record = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            if record and record.get("http"):
                return record["http"]
    raise HomeAssistantError(f"Dispositivo AWTRIX NG HTTP non disponibile: {device_name}")


def register_icon_services(hass):
    """Register icon asset actions without altering established entities/services."""
    target = {vol.Required("device"): cv.string}

    async def list_icons(call):
        api = _device_http(hass, call.data["device"])
        response = await api.request("GET", "/api/v1/files?dir=/ICONS")
        if not isinstance(response, dict) or not isinstance(response.get("files"), list):
            raise HomeAssistantError("Risposta elenco icone non valida")
        return {
            "files": sorted(
                (item for item in response["files"] if isinstance(item, dict) and isinstance(item.get("name"), str)),
                key=lambda item: item["name"].lower(),
            ),
            "usedBytes": response.get("usedBytes"),
            "totalBytes": response.get("totalBytes"),
        }

    async def rename_icon(call):
        api = _device_http(hass, call.data["device"])
        old = _validate_name(call.data["old_name"])
        new = _validate_name(call.data["new_name"])
        if old.rsplit(".", 1)[1].lower() != new.rsplit(".", 1)[1].lower():
            raise HomeAssistantError("La rinomina non può modificare l'estensione")
        await api.request("POST", "/api/v1/icons/rename", {"from": old, "to": new})

    async def delete_icon(call):
        api = _device_http(hass, call.data["device"])
        name = _validate_name(call.data["name"])
        await api.request("DELETE", "/api/v1/files?" + urlencode({"path": f"/ICONS/{name}"}))

    async def upload_icon(call):
        api = _device_http(hass, call.data["device"])
        filename = _validate_name(call.data["filename"])
        source_dir = Path(hass.config.path("www", "awtrix_icons")).resolve()
        source_file = (source_dir / filename).resolve()
        if source_file.parent != source_dir:
            raise HomeAssistantError("Percorso non ammesso")

        def read_file():
            if not source_file.is_file():
                raise HomeAssistantError(f"File non trovato in /config/www/awtrix_icons/: {filename}")
            if source_file.stat().st_size > 1024 * 1024:
                raise HomeAssistantError("Dimensione massima upload: 1 MB")
            data = source_file.read_bytes()
            if not data:
                raise HomeAssistantError("File vuoto")
            if filename.lower().endswith(".gif"):
                valid = data.startswith((b"GIF87a", b"GIF89a"))
            else:
                valid = data.startswith(b"\xff\xd8\xff")
            if not valid:
                raise HomeAssistantError("Contenuto file non coerente con GIF/JPEG")
            return data

        content = await hass.async_add_executor_job(read_file)
        form = FormData()
        form.add_field("file", content, filename=filename,
                       content_type="image/gif" if filename.lower().endswith(".gif") else "image/jpeg")
        try:
            async with async_get_clientsession(hass).post(
                api.host + "/api/v1/files?dir=/ICONS", data=form, timeout=ClientTimeout(total=25)
            ) as response:
                response.raise_for_status()
                await response.read()
        except (ClientError, TimeoutError) as exc:
            raise HomeAssistantError(f"Caricamento icona non riuscito: {exc}") from exc

    hass.services.async_register(
        DOMAIN, "icon_list", list_icons,
        schema=vol.Schema(target), supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN, "icon_rename", rename_icon,
        schema=vol.Schema({**target, vol.Required("old_name"): cv.string,
                           vol.Required("new_name"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN, "icon_delete", delete_icon,
        schema=vol.Schema({**target, vol.Required("name"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN, "icon_upload", upload_icon,
        schema=vol.Schema({**target, vol.Required("filename"): cv.string}),
    )
