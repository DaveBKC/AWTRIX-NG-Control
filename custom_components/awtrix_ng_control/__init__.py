"""AWTRIX NG Control: independent MQTT integration (initial release)."""
from __future__ import annotations
import json
import re
import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components import mqtt
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from .native_targets import entry_for_device_id
from .notification_payload import notification_payload, NOTIFICATION_FIELDS
from .const import DOMAIN, CONF_PREFIX, CONF_NAME

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "number", "switch", "button", "text", "select", "image", "light", "notify"]
TARGET = {vol.Required("device"): cv.string}
JSON_DATA = {vol.Required("data"): dict}

COMMANDS = {
    "notify": ("notify", True),
    "dismiss": ("notify/dismiss", False),
    "settings": ("settings", True),
    "switch_app": ("apps/switch", False),
    "sound": ("sound", True),
    "rtttl": ("rtttl", True),
    "play_audio": ("audio/play", True),
    "stop_audio": ("audio/stop", True),
}

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    from .live_screen import async_setup_live_screen
    await async_setup_live_screen(hass)
    if hass.services.has_service(DOMAIN, "notify"):
        return True

    def entry_for(call: ServiceCall):
        target = call.data["device"].strip().lower()
        for entry in hass.config_entries.async_entries(DOMAIN):
            if target in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
                if entry.entry_id in hass.data[DOMAIN]:
                    return entry
        raise HomeAssistantError(f"AWTRIX NG device not loaded: {target}")

    async def publish(call: ServiceCall, suffix: str, body: str):
        entry = entry_for(call)
        topic = f"{entry.data[CONF_PREFIX]}/cmd/{suffix}"
        await mqtt.async_publish(hass, topic, body, qos=0, retain=False)

    async def handle(call: ServiceCall):
        action = call.service
        if action == "command":
            suffix = call.data["command"].strip().strip("/")
            if not re.fullmatch(r"[A-Za-z0-9_/-]+", suffix) or not suffix:
                raise HomeAssistantError("Invalid command path")
            obj = call.data.get("data")
            raw = call.data.get("payload")
            if obj is not None and raw is not None:
                raise HomeAssistantError("Specify either data or payload, not both")
            body = json.dumps(obj, ensure_ascii=False) if obj is not None else (raw if raw is not None else "")
            await publish(call, suffix, body)
        elif action == "push_app":
            name = call.data["name"]
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name):
                raise HomeAssistantError("App name must be 1-32 letters, digits, underscores or hyphens")
            await publish(call, f"apps/pushed/{name}", json.dumps(call.data["data"], ensure_ascii=False))
        elif action == "remove_app":
            name = call.data["name"]
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name):
                raise HomeAssistantError("Invalid app name")
            await publish(call, f"apps/pushed/{name}", "")
        elif action == "dismiss_named":
            name = call.data["name"]
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name):
                raise HomeAssistantError("Invalid notification name")
            await publish(call, f"notify/dismiss/{name}", "")
        elif action == "radio_station":
            await publish(call, "audio/play", json.dumps({"station": call.data["station"]}, ensure_ascii=False))
        elif action == "radio_stop":
            await publish(call, "audio/stop", '{"group":"radio"}')
        elif action in ("radio_add", "radio_remove", "radio_refresh"):
            device = hass.data[DOMAIN][entry_for(call).entry_id]
            if not device.get("http"):
                raise HomeAssistantError("Configure the AWTRIX device HTTP address in integration options")
            if action == "radio_refresh":
                await device["http"].refresh()
            elif action == "radio_add":
                await device["http"].modify_station(call.data["name"], call.data["url"])
            else:
                await device["http"].modify_station(call.data["name"], None)
        elif action in ("app_refresh", "app_set_enabled", "app_set_order"):
            device = hass.data[DOMAIN][entry_for(call).entry_id]
            http = device.get("http")
            if not http:
                raise HomeAssistantError("Client HTTP non disponibile")
            if action == "app_refresh":
                await http.refresh()
            elif action == "app_set_enabled":
                from urllib.parse import quote
                name = call.data["name"]
                if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name):
                    raise HomeAssistantError("Nome applicazione non valido")
                # PUT expects a JSON boolean, not {"enabled":true}.
                await http.request("PUT", f"/api/v1/apps/{quote(name, safe='')}/enabled", call.data["enabled"])
                await http.refresh()
            else:
                # Require all currently rotating apps exactly once. This prevents
                # accidental removal/activation of apps from a partial list.
                await http.refresh()
                # Reuse the existing, verified /api/v1/ fallback instead of
                # assuming /api/v1/apps always returns the populated list.
                apps = http.apps
                if not isinstance(apps, list) or not apps:
                    raise HomeAssistantError("Impossibile leggere l'elenco applicazioni")
                rotating = [a["name"] for a in apps if isinstance(a, dict) and a.get("inLoop") and a.get("enabled") and isinstance(a.get("name"), str)]
                disabled = [a["name"] for a in apps if isinstance(a, dict) and a.get("enabled") is False and isinstance(a.get("name"), str)]
                order = call.data["order"]
                if len(order) != len(set(order)) or set(order) != set(rotating):
                    raise HomeAssistantError("L'ordine deve contenere una volta ciascuna app attualmente in rotazione: " + ", ".join(rotating))
                await http.request("PUT", "/api/v1/apps/order", {"order": order, "disabled": disabled})
                await http.refresh()
        elif action == "http_request":
            device = hass.data[DOMAIN][entry_for(call).entry_id]
            if not device.get("http"):
                raise HomeAssistantError("Configure HTTP address in integration options")
            await device["http"].request(call.data["method"], call.data["path"], call.data.get("data"))
        elif action in ("indicator_set", "indicator_clear"):
            device = hass.data[DOMAIN][entry_for(call).entry_id]
            http = device.get("http")
            if not http:
                raise HomeAssistantError("HTTP not configured for this device")
            identifier = call.data["indicator"]
            path = f"/api/v1/indicators/{identifier}"
            if action == "indicator_set":
                await http.request("PUT", path, call.data["data"])
            else:
                await http.request("DELETE", path)
        elif action == "notify_simple":
            body = {"text": call.data["message"],
                    "durationMs": call.data.get("duration", 10) * 1000}
            for source, target in (("icon", "icon"), ("color", "textColor"),
                                   ("sound", "sound")):
                if call.data.get(source):
                    body[target] = call.data[source]
            await publish(call, "notify", json.dumps(body, ensure_ascii=False))
        elif action == "switch_app":
            device = hass.data[DOMAIN][entry_for(call).entry_id]
            if device.get("http"):
                await device["http"].request("PUT", "/api/v1/apps/active", {"name": call.data["name"], "fast": True})
            else:
                await publish(call, "apps/switch", call.data["name"])
        elif action == "dismiss":
            await publish(call, "notify/dismiss", "")
        else:
            suffix = COMMANDS[action][0]
            await publish(call, suffix, json.dumps(call.data["data"], ensure_ascii=False))

    schemas = {
        "notify": vol.Schema({**TARGET, **JSON_DATA}),
        "settings": vol.Schema({**TARGET, **JSON_DATA}),
        "sound": vol.Schema({**TARGET, **JSON_DATA}),
        "rtttl": vol.Schema({**TARGET, **JSON_DATA}),
        "dismiss": vol.Schema(TARGET),
        "play_audio": vol.Schema({**TARGET, **JSON_DATA}),
        "stop_audio": vol.Schema({**TARGET, **JSON_DATA}),
        "radio_station": vol.Schema({**TARGET, vol.Required("station"): cv.string}),
        "radio_stop": vol.Schema(TARGET),
        "radio_add": vol.Schema({**TARGET, vol.Required("name"): cv.string, vol.Required("url"): cv.url}),
        "radio_remove": vol.Schema({**TARGET, vol.Required("name"): cv.string}),
        "radio_refresh": vol.Schema(TARGET),
        "app_refresh": vol.Schema(TARGET),
        "app_set_enabled": vol.Schema({**TARGET, vol.Required("name"): cv.string, vol.Required("enabled"): cv.boolean}),
        "app_set_order": vol.Schema({**TARGET, vol.Required("order"): vol.All([cv.string], vol.Length(min=1))}),
        "http_request": vol.Schema({**TARGET, vol.Required("method"): vol.In(["GET","POST","PUT","PATCH","DELETE"]), vol.Required("path"): cv.string, vol.Optional("data"): dict}),
        "switch_app": vol.Schema({**TARGET, vol.Required("name"): cv.string}),
        "indicator_set": vol.Schema({**TARGET, vol.Required("indicator"): vol.All(vol.Coerce(int), vol.Range(min=1,max=3)), vol.Required("data"): dict}),
        "indicator_clear": vol.Schema({**TARGET, vol.Required("indicator"): vol.All(vol.Coerce(int), vol.Range(min=1,max=3))}),
        "notify_simple": vol.Schema({**TARGET, vol.Required("message"): cv.string, vol.Optional("duration", default=10): vol.All(vol.Coerce(int), vol.Range(min=1,max=600)), vol.Optional("icon"): cv.string, vol.Optional("color"): cv.string, vol.Optional("sound"): cv.string}),
        "push_app": vol.Schema({**TARGET, vol.Required("name"): cv.string, **JSON_DATA}),
        "remove_app": vol.Schema({**TARGET, vol.Required("name"): cv.string}),
        "dismiss_named": vol.Schema({**TARGET, vol.Required("name"): cv.string}),
        "command": vol.Schema({**TARGET, vol.Required("command"): cv.string, vol.Optional("data"): dict, vol.Optional("payload"): cv.string}),
    }
    for key, schema in schemas.items():
        hass.services.async_register(DOMAIN, key, handle, schema=schema)
    # Device-targeted actions are additive; legacy `device: prefix` actions remain unchanged.
    async def handle_device_target(call: ServiceCall):
        # Both UI target.device_id and the old data.device_id arrive in
        # ServiceCall.data. Accept either one and reject missing targets.
        requested = call.data.get("device_id")
        if not requested:
            raise HomeAssistantError("Select an AWTRIX NG Control device as the action target")
        identifiers = [requested] if isinstance(requested, str) else requested
        if not isinstance(identifiers, list) or not identifiers or not all(isinstance(v, str) for v in identifiers):
            raise HomeAssistantError("Invalid Home Assistant device target")
        for identifier in dict.fromkeys(identifiers):
            entry = entry_for_device_id(hass, identifier)
            prefix = entry.data[CONF_PREFIX]
            if call.service == "notify_device":
                suffix = "notify"
                payload = json.dumps(notification_payload(call.data), ensure_ascii=False)
            elif call.service == "show_app_device":
                device = hass.data[DOMAIN][entry.entry_id]
                if device.get("http"):
                    await device["http"].request("PUT", "/api/v1/apps/active", {"name": call.data["name"], "fast": True})
                    continue
                suffix, payload = "apps/switch", call.data["name"]
            else:
                suffix, payload = "notify/dismiss", ""
            await mqtt.async_publish(hass, f"{prefix}/cmd/{suffix}", payload, qos=0, retain=False)

    # Home Assistant's built-in action target injects device_id into call.data.
    # The legacy data.device_id form remains supported.
    hass.services.async_register(DOMAIN, "notify_device", handle_device_target,
        schema=vol.Schema({vol.Optional("device_id"): vol.Any(cv.string, [cv.string]), vol.Required("message"): cv.string, **NOTIFICATION_FIELDS}))
    hass.services.async_register(DOMAIN, "show_app_device", handle_device_target,
        schema=vol.Schema({vol.Required("device_id"): cv.string, vol.Required("name"): cv.string}))
    hass.services.async_register(DOMAIN, "dismiss_device", handle_device_target,
        schema=vol.Schema({vol.Required("device_id"): cv.string}))
    from .icon_management import register_icon_services
    register_icon_services(hass)
    from .advanced_notifications import register_advanced_notification_services
    register_advanced_notification_services(hass)
    from .berry_scripts import register_script_services
    register_script_services(hass)
    from .audio_management import register_audio_management_services
    register_audio_management_services(hass)
    from .system_management import register_system_services
    register_system_services(hass)
    from .visual_effects import register_visual_effect_services
    register_visual_effect_services(hass)
    from .app_management import register_app_management_services
    register_app_management_services(hass)
    from .file_management import register_file_services
    register_file_services(hass)
    from .backup_management import register_backup_services
    register_backup_services(hass)
    from .maintenance import register_maintenance_services
    register_maintenance_services(hass)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    device = {"entry": entry, "state": {}, "available": False, "listeners": set(), "notification_color": "#FFFFFF", "notification_icon": ""}
    from .http_api import AwtrixHttp
    # Read legacy data too: earlier versions kept HTTP host in different places.
    host = (entry.options.get("host") or entry.data.get("host") or "").strip()
    # Existing TC002 installation: API host confirmed by the user's actual JSON responses.
    # Do not change a configured host, and do not apply this fallback to other prefixes.
    if not host and entry.data[CONF_PREFIX].lower() == 'tc002':
        host = '192.168.0.16'
        _LOGGER.warning('AWTRIX NG TC002: using confirmed HTTP host %s (HTTP option empty)', host)
    device["http"] = AwtrixHttp(hass, host, device) if host else None
    if not host:
        _LOGGER.error("AWTRIX NG %s: HTTP host not configured; open integration options and enter the device IP (e.g. 192.168.0.16)", entry.title)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device
    prefix = entry.data[CONF_PREFIX]

    @callback
    def update_state(msg):
        topic = msg.topic
        if topic == f"{prefix}/availability":
            device["available"] = msg.payload == "online"
        elif topic.startswith(f"{prefix}/state/"):
            device["available"] = True  # A live state packet proves MQTT communication.
            path = topic[len(prefix)+7:]
            try:
                value = json.loads(msg.payload)
            except (ValueError, TypeError):
                value = msg.payload
            device["state"][path] = value
            if path == "device" and isinstance(value, dict) and not device["available"]:
                device["available"] = True
        for listener in tuple(device["listeners"]):
            listener()

    @callback
    def update_event(msg):
        try:
            device["state"]["last_error"] = json.loads(msg.payload)
        except (ValueError, TypeError):
            device["state"]["last_error"] = msg.payload
        for listener in tuple(device["listeners"]):
            listener()

    unsub = await mqtt.async_subscribe(hass, f"{prefix}/state/#", update_state)
    unsub_avail = await mqtt.async_subscribe(hass, f"{prefix}/availability", update_state)
    unsub_errors = await mqtt.async_subscribe(hass, f"{prefix}/event/error", update_event)
    device["unsubs"] = [unsub, unsub_avail, unsub_errors]
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    if device["http"]:
        try:
            await device["http"].start()
        except Exception:
            _LOGGER.exception("AWTRIX NG HTTP startup failed for %s; continuing with MQTT controls", entry.title)
    # Remove only the obsolete TEXT entity left by old versions. The existing
    # SELECT entry is preserved with its original unique_id and entity_id.
    registry = er.async_get(hass)
    old_text_entity = registry.async_get_entity_id(
        "text", DOMAIN, f"{entry.entry_id}_text_app"
    )
    if old_text_entity:
        registry.async_remove(old_text_entity)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    device = hass.data[DOMAIN].pop(entry.entry_id)
    if device.get("http"):
        await device["http"].stop()
    entry.async_unload_callbacks()
    for unsub in device["unsubs"]:
        unsub()
    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
