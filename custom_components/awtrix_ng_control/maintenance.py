"""Read-only diagnostics and explicitly confirmed maintenance actions."""
from __future__ import annotations
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_PREFIX


def register_maintenance_services(hass: HomeAssistant) -> None:
    def http_for(call: ServiceCall):
        target = call.data["device"].strip().lower()
        for entry in hass.config_entries.async_entries(DOMAIN):
            if target in (entry.entry_id.lower(), entry.data[CONF_PREFIX].lower()):
                device = hass.data.get(DOMAIN, {}).get(entry.entry_id)
                if device and device.get("http"):
                    return device["http"]
        raise HomeAssistantError(f"AWTRIX NG HTTP device unavailable: {target}")

    async def health(call: ServiceCall):
        client = http_for(call)
        device = await client.request("GET", "/api/v1/device")
        if not isinstance(device, dict):
            raise HomeAssistantError("AWTRIX NG device response is not an object")
        # Do not expose credentials from /system; only documented non-sensitive state.
        fields = ("version", "hostname", "ipAddress", "wifiRssi", "uptimeSeconds", "resetReason", "boardType", "soc", "updateImage")
        output = {key: device[key] for key in fields if key in device}
        output["http_connected"] = True
        return output

    async def reboot(call: ServiceCall):
        if call.data["confirm"] is not True:
            raise HomeAssistantError("Explicit confirmation required (confirm: true)")
        client = http_for(call)
        result = await client.request("POST", "/api/v1/device/reboot")
        if isinstance(result, dict) and result.get("ok") is False:
            raise HomeAssistantError(f"AWTRIX NG refused reboot: {result}")
        # Do not poll: the device deliberately disconnects immediately after the reply.

    hass.services.async_register(DOMAIN, "device_health", health, schema=vol.Schema({vol.Required("device"): cv.string}), supports_response=SupportsResponse.ONLY)
    hass.services.async_register(DOMAIN, "device_reboot", reboot, schema=vol.Schema({vol.Required("device"): cv.string, vol.Required("confirm"): cv.boolean}))
