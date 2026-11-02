"""Resolve Home Assistant device IDs to loaded AWTRIX config entries."""
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN


def entry_for_device_id(hass, device_id):
    device = dr.async_get(hass).async_get(device_id)
    if device is None:
        raise HomeAssistantError("Unknown Home Assistant device_id")
    for domain, identifier in device.identifiers:
        if domain == DOMAIN and identifier in hass.data.get(DOMAIN, {}):
            return hass.data[DOMAIN][identifier]["entry"]
    raise HomeAssistantError("The selected device is not a loaded AWTRIX NG Control device")
