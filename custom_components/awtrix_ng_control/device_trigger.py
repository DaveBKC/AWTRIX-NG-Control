"""Button-press device triggers based on the existing binary sensors."""
from __future__ import annotations
import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import state
from homeassistant.const import CONF_DEVICE_ID, CONF_TYPE
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN
from .native_targets import entry_for_device_id

_TYPES = {"left_pressed": "left", "select_pressed": "select", "right_pressed": "right"}
TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend({vol.Required(CONF_TYPE): vol.In(_TYPES)})

async def async_get_triggers(hass, device_id):
    try:
        entry_for_device_id(hass, device_id)
    except Exception:
        return []
    return [{"platform": "device", "domain": DOMAIN, "device_id": device_id, "type": kind} for kind in _TYPES]

async def async_attach_trigger(hass, config, action, trigger_info):
    entry = entry_for_device_id(hass, config[CONF_DEVICE_ID])
    key = _TYPES[config[CONF_TYPE]]
    entity_id = er.async_get(hass).async_get_entity_id("binary_sensor", DOMAIN, f"{entry.entry_id}_binary_{key}")
    if not entity_id:
        raise ValueError(f"Button sensor {key} is not registered")
    return await state.async_attach_trigger(
        hass,
        {"platform": "state", "entity_id": entity_id, "to": "on"},
        action, trigger_info, platform_type="device",
    )
