"""Manage AWTRIX NG applications without changing their rotation order."""
from __future__ import annotations
import re
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_PREFIX

VALID_APP = re.compile(r"[A-Za-z0-9_-]{1,32}\Z")


def register_app_management_services(hass: HomeAssistant) -> None:
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
        if call.service == "app_list_http":
            # The TC002 can return an empty list on /api/v1/apps.
            await client.refresh()
            if not client.endpoint_ok.get("apps"):
                raise HomeAssistantError("Unable to read current application list")
            return {"apps": client.apps}
        name = call.data["name"].strip()
        if not VALID_APP.fullmatch(name) or name.lower() in ("active", "next", "previous", "order"):
            raise HomeAssistantError("Invalid app name")
        if call.service == "app_show_http":
            return await client.request("PUT", "/api/v1/apps/active", {"name": name, "fast": call.data.get("fast", False)})
        if call.service == "app_set_enabled":
            return await client.request("PUT", f"/api/v1/apps/{name}/enabled", call.data["enabled"])
        raise HomeAssistantError(f"Unknown app action {call.service}")

    target = {vol.Required("device"): cv.string}
    named = {**target, vol.Required("name"): cv.string}
    hass.services.async_register(DOMAIN, "app_list_http", handle, schema=vol.Schema(target), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "app_show_http", handle, schema=vol.Schema({**named, vol.Optional("fast", default=False): cv.boolean}))
