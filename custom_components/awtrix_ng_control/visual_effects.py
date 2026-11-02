"""Advanced visual effects for AWTRIX NG (HTTP API)."""
from __future__ import annotations
import voluptuous as vol
import re
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_PREFIX

TARGET = {vol.Required("device"): cv.string}


def register_visual_effect_services(hass: HomeAssistant) -> None:
    def client_for(call: ServiceCall):
        target = call.data["device"].strip().lower()
        for entry in hass.config_entries.async_entries(DOMAIN):
            if target in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
                device = hass.data.get(DOMAIN, {}).get(entry.entry_id)
                if device and device.get("http"):
                    return device["http"]
        raise HomeAssistantError(f"AWTRIX NG HTTP device unavailable: {target}")

    async def handle(call: ServiceCall):
        client = client_for(call)
        action = call.service
        if action == "visual_capabilities":
            data = await client.request("GET", "/api/v1/capabilities")
            return {key: data.get(key, []) for key in ("effects", "paletteEffects", "transitions", "overlays", "palettes")}
        if action == "visual_effect_app":
            app = call.data["name"].strip()
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", app) or app.lower() in ("active", "next", "previous", "order"):
                raise HomeAssistantError("Invalid app name")
            body = {"text": call.data["text"]}
            for source, dest in (("effect", "effect"), ("effect_speed", "effectSpeed"), ("palette", "palette"), ("overlay", "overlay"), ("duration_ms", "durationMs")):
                if source in call.data:
                    body[dest] = call.data[source]
            if "effect" not in body and "overlay" not in body:
                raise HomeAssistantError("Set effect or overlay")
            result = await client.request("PUT", "/api/v1/apps/pushed/" + app, body)
            # Side effects are explicit and independent. Preserve both old defaults.
            if call.data.get("enable_rotation", False):
                await client.request("PATCH", "/api/v1/settings", {"autoTransition": True})
            if call.data.get("show_immediately", False):
                await client.request("PUT", "/api/v1/apps/active", {"name": app})
            return result
        if action == "visual_overlay_global":
            overlay = call.data["overlay"]
            body = {"overlay": None if overlay.lower() in ("none", "off", "null") else overlay}
            if "speed" in call.data or "palette" in call.data:
                settings = {}
                if "speed" in call.data: settings["speed"] = call.data["speed"]
                if "palette" in call.data: settings["palette"] = call.data["palette"]
                body["overlaySettings"] = settings
            return await client.request("PATCH", "/api/v1/display", body)
        if action == "visual_transition":
            return await client.request("PATCH", "/api/v1/settings", {
                "transitionEffect": call.data["effect"],
                "transitionDurationMs": call.data["duration_ms"]})
        raise HomeAssistantError(f"Unsupported visual effect action: {action}")

    hass.services.async_register(DOMAIN, "visual_capabilities", handle,
        schema=vol.Schema(TARGET), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "visual_effect_app", handle, schema=vol.Schema({
        **TARGET, vol.Required("name"): cv.string, vol.Required("text"): cv.string,
        vol.Optional("effect"): cv.string,
        vol.Optional("effect_speed"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=10)),
        vol.Optional("palette"): cv.string, vol.Optional("overlay"): cv.string,
        vol.Optional("show_immediately", default=False): cv.boolean,
        vol.Optional("enable_rotation", default=False): cv.boolean,
        vol.Optional("duration_ms"): vol.All(vol.Coerce(int), vol.Range(min=100, max=3600000)),
    }))
    hass.services.async_register(DOMAIN, "visual_overlay_global", handle, schema=vol.Schema({
        **TARGET, vol.Required("overlay"): cv.string,
        vol.Optional("speed"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=10)),
        vol.Optional("palette"): cv.string,
    }))
    hass.services.async_register(DOMAIN, "visual_transition", handle, schema=vol.Schema({
        **TARGET, vol.Required("effect"): cv.string,
        vol.Required("duration_ms"): vol.All(vol.Coerce(int), vol.Range(min=0, max=10000)),
    }))
