"""Validate AWTRIX notification options shared by native device actions and services."""
from __future__ import annotations

import re
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# MQTT AWTRIX durationMs is milliseconds; this API exposes duration in seconds.
NOTIFICATION_FIELDS = {
    vol.Optional("title"): cv.string,
    vol.Optional("duration"): vol.All(vol.Coerce(int), vol.Range(min=1, max=600)),
    vol.Optional("icon"): cv.string,
    vol.Optional("color"): cv.string,
    vol.Optional("sound"): cv.string,
    vol.Optional("scroll"): cv.boolean,
    vol.Optional("wakeup"): cv.boolean,
    vol.Optional("stack"): cv.boolean,
    vol.Optional("data"): dict,
}

# Only recognized payload keys may be added via the advanced data dictionary.
_ALLOWED_EXTRA = {
    "name", "durationMs", "icon", "sound", "textColor", "scroll", "wakeup",
    "stack", "repeat", "hold", "font", "align", "background", "color",
    "rainbow", "effect", "effectSettings", "layout", "soundVolume",
}

def title_message_layout(title: str, message: str, icon: str | None = None,
                         color: str | None = None) -> dict:
    """Render title and body on separate rows of the TC002 52x16 display."""
    offset = 16 if icon else 0
    width = 52 - offset
    regions = []
    if icon:
        regions.append({"id": "icon", "box": [0, 0, 16, 16], "icon": icon})
    regions.extend([
        {"id": "title", "box": [offset, 0, width, 8], "text": title,
         "font": "matrix-light6", "color": "#FFCC33"},
        {"id": "message", "box": [offset, 8, width, 8], "text": message,
         "font": "matrix-light6", "color": color or "#FFFFFF"},
    ])
    return {"version": 1, "regions": regions}


def notification_payload(data: dict) -> dict:
    message = data["message"]
    title = data.get("title")
    result = {"text": f"{title}: {message}" if title else message}
    extra = data.get("data", {})
    if not isinstance(extra, dict):
        raise vol.Invalid("data must be an object")
    unknown = set(extra) - _ALLOWED_EXTRA
    if unknown:
        raise vol.Invalid("Unknown AWTRIX notification options: " + ", ".join(sorted(unknown)))
    result.update(extra)
    if "duration" in data:
        result["durationMs"] = data["duration"] * 1000
    for name, target in (("icon", "icon"), ("color", "textColor"), ("sound", "sound"),
                         ("scroll", "scroll"), ("wakeup", "wakeup"), ("stack", "stack")):
        if name in data:
            result[target] = data[name]
    if "durationMs" in result:
        if isinstance(result["durationMs"], bool) or not isinstance(result["durationMs"], int) or not 100 <= result["durationMs"] <= 600000:
            raise vol.Invalid("durationMs must be between 100 and 600000 milliseconds")
    if "name" in result and not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", str(result["name"])):
        raise vol.Invalid("Invalid notification name")
    # Default TC002 layout for titled notifications. Explicit custom layouts win.
    if title and "layout" not in result:
        result["layout"] = title_message_layout(title, message, result.pop("icon", None),
                                                 result.pop("textColor", None))
        # In layout mode drawing keys must reside inside regions.
        result.pop("text", None)
        result.pop("scroll", None)
        result.pop("color", None)
    return result
