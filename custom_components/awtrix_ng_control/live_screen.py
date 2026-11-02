"""On-demand AWTRIX 3 / AWTRIX NG live screen relay (no camera entity)."""
from __future__ import annotations
import asyncio
import json
import logging
import re
import voluptuous as vol
from homeassistant.components import mqtt, websocket_api
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)
# One bounded MQTT consumer and polling task per actively viewed display.
_sessions: dict[tuple[str, str], dict] = {}


def _parse(payload, firmware):
    """Normalize AWTRIX screen frames into {width,height,pixels}."""
    try:
        obj = json.loads(payload)
        if isinstance(obj, dict):
            w, h, px = obj.get("width"), obj.get("height"), obj.get("pixels")
        elif firmware == "awtrix3" and isinstance(obj, list):
            w, h, px = 32, 8, obj
        else:
            return None
        if (not isinstance(w, int) or isinstance(w, bool) or
            not isinstance(h, int) or isinstance(h, bool) or
            w < 1 or h < 1 or w * h > 4096 or not isinstance(px, list) or len(px) != w*h):
            return None
        # Colors are unsigned 24 bit RGB integers.
        if not all(isinstance(p, int) and not isinstance(p, bool) and 0 <= p <= 0xFFFFFF for p in px):
            return None
        return {"width": w, "height": h, "pixels": px}
    except (ValueError, TypeError):
        return None


async def _stop(hass: HomeAssistant, key, session):
    if _sessions.get(key) is not session or session["viewers"]:
        return
    _sessions.pop(key, None)
    session["task"].cancel()
    try:
        await session["task"]
    except asyncio.CancelledError:
        pass
    session["unsub"]()


@websocket_api.websocket_command({
    vol.Required("type"): "awtrix_ng_control/live_screen",
    vol.Required("prefix"): vol.All(str, vol.Match(r"^[A-Za-z0-9_-]{1,64}$")),
    vol.Required("firmware"): vol.In(("awtrix3", "awtrix_ng")),
})
@websocket_api.async_response
async def ws_live_screen(hass, connection, msg):
    """Subscribe user to screen frames, poll only while there are viewers."""
    if not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Administrator required")
        return
    key = (msg["prefix"], msg["firmware"])
    session = _sessions.get(key)
    if session is None:
        prefix, firmware = key
        screen_topic = f"{prefix}/screen" if firmware == "awtrix3" else f"{prefix}/state/screen"
        command_topic = f"{prefix}/sendscreen" if firmware == "awtrix3" else f"{prefix}/cmd/screen/get"
        session = {"viewers": {}, "last": None}

        @callback
        def on_frame(mqtt_msg):
            frame = _parse(mqtt_msg.payload, firmware)
            if frame is None:
                return
            session["last"] = frame
            for conn, ident in tuple(session["viewers"].values()):
                try:
                    conn.send_event(ident, frame)
                except Exception:
                    _LOGGER.debug("Live screen viewer disconnected", exc_info=True)

        try:
            session["unsub"] = await mqtt.async_subscribe(hass, screen_topic, on_frame)
        except Exception as err:
            connection.send_error(msg["id"], "mqtt_error", str(err))
            return

        async def poll():
            try:
                while True:
                    await mqtt.async_publish(hass, command_topic, "", qos=0, retain=False)
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                raise
            except Exception:
                _LOGGER.exception("Live screen polling failed for %s", prefix)

        session["task"] = hass.async_create_task(poll())
        _sessions[key] = session
    viewer_key = (id(connection), msg["id"])
    session["viewers"][viewer_key] = (connection, msg["id"])

    @callback
    def unsubscribe():
        session["viewers"].pop(viewer_key, None)
        if not session["viewers"]:
            hass.async_create_task(_stop(hass, key, session))

    connection.subscriptions[msg["id"]] = unsubscribe
    connection.send_result(msg["id"])
    if session["last"]:
        connection.send_event(msg["id"], session["last"])


async def async_setup_live_screen(hass: HomeAssistant):
    """Expose the card asset and the screen WebSocket subscription."""
    from pathlib import Path
    from homeassistant.components.http import StaticPathConfig
    path = Path(__file__).parent / "www" / "awtrix-live-screen.js"
    await hass.http.async_register_static_paths([
        StaticPathConfig("/awtrix-ng-control/awtrix-live-screen.js", str(path), False)
    ])
    websocket_api.async_register_command(hass, ws_live_screen)
