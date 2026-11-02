"""Safe asset-folder file management for AWTRIX NG."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlencode, quote

from aiohttp import ClientError, ClientTimeout, FormData
import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .icon_management import _device_http
from .const import DOMAIN

FOLDERS = ("ICONS", "MELODIES", "PALETTES", "MP3")
NAME = re.compile(r"^[A-Za-z0-9_-]{1,32}\.(?:gif|jpg|jpeg|txt|mp3|rtttl)$", re.I)
MAX_BYTES = 2 * 1024 * 1024


def _folder(folder):
    folder = folder.strip().upper().lstrip("/")
    if folder not in FOLDERS:
        raise HomeAssistantError("Unsupported asset folder (ICONS, MELODIES, PALETTES, MP3)")
    return folder


def _name(folder, name):
    if not NAME.fullmatch(name) or name in (".", ".."):
        raise HomeAssistantError("Invalid file name")
    suffix = Path(name).suffix.lower()
    allowed = {"ICONS": {".gif", ".jpg", ".jpeg"},
               "MELODIES": {".txt", ".rtttl"},
               "PALETTES": {".txt"}, "MP3": {".mp3"}}
    if suffix not in allowed[folder]:
        raise HomeAssistantError(f"Unsupported extension for {folder}: {suffix}")
    return name


def _check_bytes(folder, name, payload):
    if not payload or len(payload) > MAX_BYTES:
        raise HomeAssistantError("Empty file or exceeds 2 MB transfer limit")
    extension = Path(name).suffix.lower()
    if folder == "ICONS":
        okay = payload.startswith((b"GIF87a", b"GIF89a")) if extension == ".gif" else payload.startswith(b"\xff\xd8\xff")
        if not okay:
            raise HomeAssistantError("Not a GIF or JPEG file")
    elif folder == "MP3":
        if not (payload.startswith(b"ID3") or (len(payload) > 1 and payload[0] == 0xff and payload[1] & 0xe0 == 0xe0)):
            raise HomeAssistantError("Not an MP3 file")
    elif folder == "PALETTES":
        try:
            colors = payload.decode("utf-8").splitlines()
        except UnicodeError as exc:
            raise HomeAssistantError("Palette must be UTF-8") from exc
        if not colors or any(not re.fullmatch(r"#?[a-fA-F0-9]{6}", x.strip()) for x in colors):
            raise HomeAssistantError("Palette must contain one RRGGBB color per line")
    elif folder == "MELODIES":
        try:
            payload.decode("utf-8")
        except UnicodeError as exc:
            raise HomeAssistantError("Melody must be UTF-8") from exc


def register_file_services(hass):
    target = {vol.Required("device"): cv.string}
    destination = {vol.Required("folder"): vol.In(FOLDERS), vol.Required("filename"): cv.string}

    async def list_files(call):
        folder = _folder(call.data["folder"])
        api = _device_http(hass, call.data["device"])
        result = await api.request("GET", "/api/v1/files?" + urlencode({"dir": "/" + folder}))
        if not isinstance(result, dict) or not isinstance(result.get("files"), list):
            raise HomeAssistantError("Invalid file listing response")
        return {"folder": folder, "files": sorted(result["files"], key=lambda x: str(x.get("name", "")).lower()),
                "usedBytes": result.get("usedBytes"), "totalBytes": result.get("totalBytes")}

    async def upload_file(call):
        folder = _folder(call.data["folder"])
        name = _name(folder, call.data["filename"])
        path = Path(hass.config.path("awtrix_ng_files", folder, name))
        def read():
            if not path.is_file() or path.is_symlink():
                raise HomeAssistantError(f"Place the file in /config/awtrix_ng_files/{folder}/{name}")
            if path.stat().st_size > MAX_BYTES:
                raise HomeAssistantError("File too large")
            data = path.read_bytes()
            _check_bytes(folder, name, data)
            return data
        payload = await hass.async_add_executor_job(read)
        api = _device_http(hass, call.data["device"])
        form = FormData()
        form.add_field("file", payload, filename=name, content_type="application/octet-stream")
        try:
            async with async_get_clientsession(hass).post(api.host + "/api/v1/files?" + urlencode({"dir": "/" + folder}),
                                                         data=form, timeout=ClientTimeout(total=40)) as resp:
                detail = await resp.text()
                if resp.status >= 400:
                    raise HomeAssistantError(f"AWTRIX upload HTTP {resp.status}: {detail[:400]}")
        except (ClientError, TimeoutError) as exc:
            raise HomeAssistantError(f"AWTRIX upload error: {exc}") from exc

    async def delete_file(call):
        folder = _folder(call.data["folder"])
        name = _name(folder, call.data["filename"])
        api = _device_http(hass, call.data["device"])
        return await api.request("DELETE", "/api/v1/files?" + urlencode({"path": f"/{folder}/{name}"}))

    async def download_file(call):
        folder = _folder(call.data["folder"])
        name = _name(folder, call.data["filename"])
        api = _device_http(hass, call.data["device"])
        url = api.host + "/" + folder + "/" + quote(name, safe="")
        try:
            async with async_get_clientsession(hass).get(url, timeout=ClientTimeout(total=30)) as resp:
                if resp.status >= 400:
                    raise HomeAssistantError(f"AWTRIX download HTTP {resp.status}")
                # Check Content-Length before downloading, and actual size afterward.
                if int(resp.headers.get("Content-Length", "0")) > MAX_BYTES:
                    raise HomeAssistantError("File exceeds transfer limit")
                payload = await resp.content.read(MAX_BYTES + 1)
        except (ClientError, TimeoutError) as exc:
            raise HomeAssistantError(f"AWTRIX download error: {exc}") from exc
        _check_bytes(folder, name, payload)
        path = Path(hass.config.path("awtrix_ng_downloads", folder, name))
        def save():
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.is_symlink():
                raise HomeAssistantError("Refusing symbolic-link destination")
            # Never overwrite a previous downloaded copy.
            with path.open("xb") as file:
                file.write(payload)
            return str(path)
        try:
            saved = await hass.async_add_executor_job(save)
        except FileExistsError as exc:
            raise HomeAssistantError("File already downloaded: delete or rename the local copy first") from exc
        return {"folder": folder, "filename": name, "local_path": saved, "bytes": len(payload)}

    schema = vol.Schema({**target, **destination})
    hass.services.async_register(DOMAIN, "file_list", list_files,
        schema=vol.Schema({**target, vol.Required("folder"): vol.In(FOLDERS)}), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "file_upload", upload_file, schema=schema)
    hass.services.async_register(DOMAIN, "file_delete", delete_file, schema=schema)
    hass.services.async_register(DOMAIN, "file_download", download_file,
                                 schema=schema, supports_response=SupportsResponse.ONLY)
