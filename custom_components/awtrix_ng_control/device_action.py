"""Native actions in Home Assistant's device automation editor."""
from __future__ import annotations
import json
import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_ACTION_BASE_SCHEMA
from homeassistant.components import mqtt
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_PREFIX
from .native_targets import entry_for_device_id
from .notification_payload import notification_payload, NOTIFICATION_FIELDS

_TYPES = {"send_notification", "show_app", "dismiss_notification"}
ACTION_SCHEMA = DEVICE_ACTION_BASE_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In(_TYPES),
    vol.Optional("message"): cv.string,
    vol.Optional("app_name"): cv.string,
    **NOTIFICATION_FIELDS,
})

async def async_get_actions(hass, device_id):
    try:
        entry_for_device_id(hass, device_id)
    except Exception:
        return []
    return [{"domain": DOMAIN, "device_id": device_id, "type": kind} for kind in sorted(_TYPES)]

async def async_get_action_capabilities(hass, config):
    kind = config[CONF_TYPE]
    if kind == "send_notification":
        return {"extra_fields": vol.Schema({vol.Required("message"): cv.string, **NOTIFICATION_FIELDS})}
    if kind == "show_app":
        return {"extra_fields": vol.Schema({vol.Required("app_name"): cv.string})}
    return {}

async def async_call_action_from_config(hass, config, variables, context):
    entry = entry_for_device_id(hass, config[CONF_DEVICE_ID])
    prefix = entry.data[CONF_PREFIX]
    kind = config[CONF_TYPE]
    if kind == "send_notification":
        message = config["message"]
        suffix, payload = "notify", json.dumps(notification_payload(config), ensure_ascii=False)
    elif kind == "show_app":
        name = config["app_name"]
        device = hass.data[DOMAIN][entry.entry_id]
        if device.get("http"):
            await device["http"].request("PUT", "/api/v1/apps/active", {"name": name, "fast": True})
            return
        suffix, payload = "apps/switch", name
    else:
        suffix, payload = "notify/dismiss", ""
    await mqtt.async_publish(hass, f"{prefix}/cmd/{suffix}", payload, qos=0, retain=False)
