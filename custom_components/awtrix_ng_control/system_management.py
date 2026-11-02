"""Read-only diagnostics and controlled mood-light functions for AWTRIX NG."""
from __future__ import annotations
import re
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_PREFIX

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

def register_system_services(hass: HomeAssistant) -> None:
    def http_for(call: ServiceCall):
        target = call.data["device"].strip().lower()
        for entry in hass.config_entries.async_entries(DOMAIN):
            if target in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
                device = hass.data.get(DOMAIN, {}).get(entry.entry_id)
                if device and device.get("http"):
                    return device["http"]
        raise HomeAssistantError(f"AWTRIX NG HTTP device unavailable: {target}")

    async def handle(call: ServiceCall):
        client = http_for(call)
        action = call.service
        if action == "device_info":
            result = await client.request("GET", "/api/v1/device")
        elif action == "system_info":
            result = await client.request("GET", "/api/v1/system")
        elif action == "device_logs":
            result = await client.request("GET", "/api/v1/logs")
        elif action == "device_capabilities":
            result = await client.request("GET", "/api/v1/capabilities")
        elif action == "moodlight_off":
            result = await client.request("DELETE", "/api/v1/display/moodlight")
        elif action == "moodlight_set":
            body = {}
            if "color" in call.data:
                color = call.data["color"].strip()
                if not HEX.fullmatch(color):
                    raise HomeAssistantError("Color must be #RRGGBB")
                body["color"] = color
            if "kelvin" in call.data:
                body["kelvin"] = call.data["kelvin"]
            if "brightness" in call.data:
                body["brightness"] = call.data["brightness"]
            if not body:
                raise HomeAssistantError("Set at least one of color, kelvin or brightness")
            result = await client.request("PUT", "/api/v1/display/moodlight", body)
        else:
            raise HomeAssistantError(f"Unsupported service: {action}")
        # Response data makes read-only actions usable in Developer Tools and scripts.
        if isinstance(result, dict):
            return result
        if isinstance(result, list):
            return {"items": result}
        if isinstance(result, bytes):
            return {"text": result.decode("utf-8", errors="replace")}
        return {"result": str(result)}

    target = {vol.Required("device"): cv.string}
    for name in ("device_info", "system_info", "device_logs", "device_capabilities", "moodlight_off"):
        hass.services.async_register(DOMAIN, name, handle, schema=vol.Schema(target), supports_response=(SupportsResponse.ONLY if name in ("device_info", "system_info", "device_logs", "device_capabilities") else SupportsResponse.NONE))
    hass.services.async_register(DOMAIN, "moodlight_set", handle, schema=vol.Schema({
        **target,
        vol.Optional("color"): cv.string,
        vol.Optional("kelvin"): vol.All(vol.Coerce(int), vol.Range(min=1000,max=40000)),
        vol.Optional("brightness"): vol.All(vol.Coerce(int), vol.Range(min=0,max=255)),
    }))
