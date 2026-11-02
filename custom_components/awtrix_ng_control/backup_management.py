"""Conservative AWTRIX NG backups: read-only export, inspection and opt-in asset restore.

This is an integration-specific archive, NOT the firmware's native restore ZIP.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

import voluptuous as vol
from aiohttp import ClientError, ClientTimeout, FormData
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .icon_management import _device_http
from .berry_scripts import _text_request, _check_install
from .file_management import FOLDERS, _name, _check_bytes
from .const import DOMAIN

MAX_FILE = 2 * 1024 * 1024
MAX_ARCHIVE = 18 * 1024 * 1024
BASENAME = re.compile(r"[A-Za-z0-9_-]{1,48}\Z")


def _archive_name(value):
    if not BASENAME.fullmatch(value):
        raise HomeAssistantError("Backup name: 1-48 letters, digits, _ or -")
    return value


def _get_path(hass, name):
    return Path(hass.config.path("awtrix_ng_backups", name + ".zip"))


async def _read_remote(hass, api, path):
    if not path.startswith("/") or ".." in path or "://" in path:
        raise HomeAssistantError("Invalid device path")
    try:
        async with async_get_clientsession(hass).get(api.host + path, timeout=ClientTimeout(total=25)) as response:
            if response.status != 200:
                raise HomeAssistantError(f"AWTRIX GET {path}: HTTP {response.status}")
            if int(response.headers.get("Content-Length", "0")) > MAX_FILE:
                raise HomeAssistantError(f"AWTRIX file too large: {path}")
            data = await response.content.read(MAX_FILE + 1)
            if len(data) > MAX_FILE:
                raise HomeAssistantError(f"AWTRIX file too large: {path}")
            return data
    except (ClientError, TimeoutError) as exc:
        raise HomeAssistantError(f"AWTRIX download error: {exc}") from exc


def _validated_archive(blob):
    if len(blob) > MAX_ARCHIVE:
        raise HomeAssistantError("Backup exceeds 18 MiB")
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = z.namelist()
            if not names or names[0] != "manifest.json" or len(names) != len(set(names)):
                raise HomeAssistantError("Invalid archive manifest or duplicate entries")
            if len(names) > 512 or any(n.startswith("/") or ".." in n.split("/") or "\\" in n for n in names):
                raise HomeAssistantError("Unsafe archive entries")
            manifest = json.loads(z.read("manifest.json"))
            if manifest.get("format") != "awtrix-ng-control-backup" or manifest.get("version") != 1:
                raise HomeAssistantError("Not a compatible AWTRIX NG Control backup")
            expected = manifest.get("files")
            if not isinstance(expected, dict) or set(names[1:]) != set(expected):
                raise HomeAssistantError("Archive manifest does not match contents")
            total = 0
            for name in names[1:]:
                meta = expected[name]
                if not isinstance(meta, dict) or not isinstance(meta.get("sha256"), str):
                    raise HomeAssistantError("Invalid checksum entry")
                info = z.getinfo(name)
                if info.file_size > MAX_FILE or (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise HomeAssistantError(f"Unsafe or oversized file: {name}")
                data = z.read(name)
                total += len(data)
                if total > MAX_ARCHIVE or len(data) != meta.get("size") or hashlib.sha256(data).hexdigest() != meta["sha256"]:
                    raise HomeAssistantError(f"Backup corrupted: {name}")
            return manifest
    except (zipfile.BadZipFile, KeyError, ValueError, TypeError, UnicodeError) as exc:
        raise HomeAssistantError(f"Invalid backup: {exc}") from exc



async def _populated_apps(api):
    """Use the populated app list; some AWTRIX NG versions return [] at /apps."""
    errors = []
    for endpoint in ("/api/v1/", "/api/v1/apps"):
        try:
            reply = await api.request("GET", endpoint)
            items = reply if isinstance(reply, list) else reply.get("apps") if isinstance(reply, dict) else None
            if isinstance(items, list) and any(isinstance(a, dict) and isinstance(a.get("name"), str) for a in items):
                return items
            errors.append(f"{endpoint}: no named applications")
        except HomeAssistantError as exc:
            errors.append(f"{endpoint}: {exc}")
    raise HomeAssistantError("Cannot verify installed applications: " + "; ".join(errors))

def register_backup_services(hass):
    target = {vol.Required("device"): cv.string}
    name_field = {vol.Required("name"): cv.string}

    async def create(call):
        api = _device_http(hass, call.data["device"])
        name = _archive_name(call.data["name"])
        folders = call.data.get("folders", list(FOLDERS))
        include_settings = call.data.get("settings", True)
        include_scripts = call.data.get("scripts", True)
        collected = {}
        for folder in folders:
            listing = await api.request("GET", "/api/v1/files?" + urlencode({"dir": "/" + folder}))
            if not isinstance(listing, dict) or not isinstance(listing.get("files"), list):
                raise HomeAssistantError(f"Invalid listing: {folder}")
            for item in listing["files"]:
                filename = _name(folder, item["name"])
                contents = await _read_remote(hass, api, f"/{folder}/{quote(filename, safe='')}")
                _check_bytes(folder, filename, contents)
                collected[f"{folder}/{filename}"] = contents
        if include_settings:
            for key, path in (("settings", "/api/v1/settings"), ("system", "/api/v1/system"), ("stations", "/api/v1/audio/stations")):
                result = await api.request("GET", path)
                if not isinstance(result, dict):
                    raise HomeAssistantError(f"Unexpected {key} response")
                # No secrets request. Exclude any accidentally returned passwords.
                result = {k:v for k,v in result.items() if not any(token in k.lower() for token in ("pass", "secret", "token", "apikey"))}
                collected[f"metadata/{key}.json"] = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
        if include_scripts:
            entries = await _populated_apps(api)
            # Only apps positively identified as script apps are copied.
            for app in entries:
                if not isinstance(app, dict) or not isinstance(app.get("name"), str):
                    continue
                if str(app.get("type", app.get("origin", ""))).lower() not in ("script", "berry"):
                    continue
                script_name = app["name"]
                if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", script_name):
                    continue
                source = await _read_remote(hass, api, "/api/v1/apps/script/" + quote(script_name, safe=""))
                collected[f"SCRIPTS/{script_name}.ax"] = source
                config = await api.request("GET", f"/api/v1/apps/{quote(script_name, safe='')}/config")
                if not isinstance(config, dict) or not isinstance(config.get("fields"), list):
                    raise HomeAssistantError(f"Cannot back up script configuration: {script_name}")
                safe_settings = {}
                for field in config["fields"]:
                    if not isinstance(field, dict) or not isinstance(field.get("key"), str):
                        continue
                    key = field["key"]
                    if any(word in key.lower() for word in ("pass", "secret", "token", "apikey", "credential", "auth", "wifi")):
                        continue
                    if "value" in field and isinstance(field["value"], (str, int, float, bool)):
                        safe_settings[key] = field["value"]
                collected[f"SCRIPT_CONFIG/{script_name}.json"] = json.dumps(safe_settings, ensure_ascii=False).encode("utf-8")
        if not collected:
            raise HomeAssistantError("Nothing selected for backup")
        manifest = {"format":"awtrix-ng-control-backup", "version":1,
                    "created":datetime.now(timezone.utc).isoformat(), "device":call.data["device"],
                    "files":{key:{"sha256":hashlib.sha256(value).hexdigest(), "size":len(value)} for key,value in collected.items()},
                    "notes":"Integration archive. Not compatible with firmware-native /api/v1/restore. Secrets and script sounds are excluded."}
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_STORED) as zipout:
            zipout.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            for key, value in collected.items():
                zipout.writestr(key, value)
        content = mem.getvalue()
        _validated_archive(content)
        dest = _get_path(hass, name)
        def save():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as file:
                file.write(content)
        try:
            await hass.async_add_executor_job(save)
        except FileExistsError as exc:
            raise HomeAssistantError("Backup already exists; choose a new name") from exc
        return {"path":str(dest), "files":len(collected), "bytes":len(content), "secrets_included":False}

    async def inspect(call):
        name = _archive_name(call.data["name"])
        dest = _get_path(hass, name)
        def read():
            if dest.is_symlink() or not dest.is_file():
                raise HomeAssistantError("Backup not found")
            return dest.read_bytes()
        blob = await hass.async_add_executor_job(read)
        manifest = _validated_archive(blob)
        return {"name":name, "created":manifest.get("created"), "files":list(manifest["files"]),
                "file_count":len(manifest["files"]), "bytes":len(blob), "valid":True,
                "note":"Restore supports assets, Berry sources and options, and selected display settings. Not a native firmware backup."}

    async def restore(call):
        name = _archive_name(call.data["name"])
        folder = call.data["folder"]
        if call.data.get("confirm") is not True:
            raise HomeAssistantError("Set confirm: true to restore asset files")
        dest = _get_path(hass, name)
        def read():
            if dest.is_symlink() or not dest.is_file():
                raise HomeAssistantError("Backup not found")
            return dest.read_bytes()
        blob = await hass.async_add_executor_job(read)
        manifest = _validated_archive(blob)
        keys = [key for key in manifest["files"] if key.startswith(folder + "/") and key.count("/") == 1]
        if not keys:
            raise HomeAssistantError("No files for selected folder")
        api = _device_http(hass, call.data["device"])
        listing = await api.request("GET", "/api/v1/files?" + urlencode({"dir": "/" + folder}))
        if not isinstance(listing, dict) or not isinstance(listing.get("files"), list):
            raise HomeAssistantError("Unable to check existing files")
        existing = {item["name"] for item in listing["files"] if isinstance(item, dict) and isinstance(item.get("name"), str)}
        collisions = sorted(key for key in keys if key.split("/",1)[1] in existing)
        if collisions:
            raise HomeAssistantError("Restore refused: files already exist: " + ", ".join(collisions[:10]))
        completed = []
        with zipfile.ZipFile(io.BytesIO(blob)) as zipped:
            for key in keys:
                filename = _name(folder, key.split("/",1)[1])
                payload = zipped.read(key)
                _check_bytes(folder, filename, payload)
                form = FormData()
                form.add_field("file", payload, filename=filename, content_type="application/octet-stream")
                try:
                    async with async_get_clientsession(hass).post(api.host + "/api/v1/files?" + urlencode({"dir":"/" + folder}), data=form, timeout=ClientTimeout(total=45)) as response:
                        response_text = await response.text()
                        if response.status >= 400:
                            raise HomeAssistantError(f"Partial restore {completed}; failed at {filename}: HTTP {response.status}: {response_text[:200]}")
                except (ClientError, TimeoutError) as exc:
                    raise HomeAssistantError(f"Partial restore {completed}; failed at {filename}: {exc}") from exc
                completed.append(filename)
        return {"folder":folder, "restored":completed, "count":len(completed)}

    async def restore_script(call):
        """Restore a script only when it is absent, plus optionally its saved options."""
        if call.data.get("confirm") is not True:
            raise HomeAssistantError("Set confirm: true")
        name = _archive_name(call.data["name"])
        script = call.data["script"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", script):
            raise HomeAssistantError("Invalid Berry script name")
        path = _get_path(hass, name)
        def load():
            if path.is_symlink() or not path.is_file():
                raise HomeAssistantError("Backup not found")
            return path.read_bytes()
        blob = await hass.async_add_executor_job(load)
        manifest = _validated_archive(blob)
        source_key = f"SCRIPTS/{script}.ax"
        config_key = f"SCRIPT_CONFIG/{script}.json"
        if source_key not in manifest["files"]:
            raise HomeAssistantError(f"Script {script} is not included in this backup")
        api = _device_http(hass, call.data["device"])
        apps = await _populated_apps(api)
        if any(isinstance(a, dict) and a.get("name") == script for a in apps):
            raise HomeAssistantError("Script exists on device: restore refused (no overwrite)")
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            try:
                source = z.read(source_key).decode("utf-8")
            except UnicodeDecodeError as exc:
                raise HomeAssistantError("Berry source is not UTF-8") from exc
            if not source or len(source.encode("utf-8")) > 256*1024:
                raise HomeAssistantError("Invalid source size")
            options = json.loads(z.read(config_key)) if config_key in manifest["files"] else None
        if options is not None and not isinstance(options, dict):
            raise HomeAssistantError("Corrupted script options")
        response = await _text_request(hass, api, "PUT", f"/api/v1/apps/script/{quote(script, safe='')}", source)
        _check_install(response)
        result = {"script":script,"installed":True,"config_restored":False}
        if call.data.get("restore_options", True) and options:
            try:
                config = await api.request("GET", f"/api/v1/apps/{quote(script, safe='')}/config")
                fields = config.get("fields") if isinstance(config, dict) else None
                if not isinstance(fields, list):
                    raise HomeAssistantError("Script options schema unavailable")
                known = {x["key"] for x in fields if isinstance(x, dict) and isinstance(x.get("key"), str)}
                unknown = set(options) - known
                if unknown:
                    raise HomeAssistantError("Unknown script options: " + ", ".join(sorted(unknown)))
                result["options_response"] = await api.request("PATCH", f"/api/v1/apps/{quote(script, safe='')}/config", options)
                result["config_restored"] = True
            except Exception as exc:
                raise HomeAssistantError(f"Script {script} INSTALLED, but configuration restore FAILED: {exc}") from exc
        await api.refresh()
        return result

    async def restore_settings(call):
        """Apply saved display settings only; never network, system or credentials."""
        if call.data.get("confirm") is not True:
            raise HomeAssistantError("Set confirm: true")
        name = _archive_name(call.data["name"])
        path = _get_path(hass, name)
        def load():
            if path.is_symlink() or not path.is_file():
                raise HomeAssistantError("Backup not found")
            return path.read_bytes()
        blob = await hass.async_add_executor_job(load)
        manifest = _validated_archive(blob)
        key = "metadata/settings.json"
        if key not in manifest["files"]:
            raise HomeAssistantError("Display settings not present in backup")
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            data = json.loads(z.read(key))
        if not isinstance(data, dict):
            raise HomeAssistantError("Invalid settings payload")
        # Explicit opt-in key allowlist; unknown keys are intentionally ignored.
        allowed = {"brightness", "autoTransition", "appDurationMs", "transition", "transitionTime", "color", "volume", "radioVolume", "alertVolume", "appVolume"}
        filtered = {k:v for k,v in data.items() if k in allowed and isinstance(v,(str,int,float,bool))}
        # Avoid sending arbitrary values to the firmware from an imported archive.
        for k in ("brightness", "volume", "radioVolume", "alertVolume", "appVolume"):
            if k in filtered and (type(filtered[k]) is not int or not 0 <= filtered[k] <= (255 if k == "brightness" else 100)):
                raise HomeAssistantError(f"Invalid backed-up setting: {k}")
        if "autoTransition" in filtered and type(filtered["autoTransition"]) is not bool:
            raise HomeAssistantError("Invalid backed-up setting: autoTransition")
        if not filtered:
            raise HomeAssistantError("No supported display settings in backup")
        api = _device_http(hass, call.data["device"])
        response = await api.request("PATCH", "/api/v1/settings", filtered)
        await api.refresh()
        return {"restored_keys":sorted(filtered),"response":response,"skipped_keys":sorted(set(data)-set(filtered))}

    hass.services.async_register(DOMAIN, "backup_create", create,
       schema=vol.Schema({**target, **name_field, vol.Optional("folders", default=list(FOLDERS)): vol.All([vol.In(FOLDERS)], vol.Length(min=1)),
                          vol.Optional("settings", default=True):cv.boolean, vol.Optional("scripts", default=True):cv.boolean}),
       supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "backup_inspect", inspect,
       schema=vol.Schema(name_field), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "backup_restore_files", restore,
       schema=vol.Schema({**target, **name_field, vol.Required("folder"):vol.In(FOLDERS), vol.Required("confirm"):cv.boolean}),
       supports_response=SupportsResponse.ONLY)

    hass.services.async_register(DOMAIN, "backup_restore_script", restore_script,
        schema=vol.Schema({**target, **name_field, vol.Required("script"):cv.string,
                           vol.Required("confirm"):cv.boolean, vol.Optional("restore_options", default=True):cv.boolean}),
        supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "backup_restore_settings", restore_settings,
        schema=vol.Schema({**target, **name_field, vol.Required("confirm"):cv.boolean}),
        supports_response=SupportsResponse.ONLY)
