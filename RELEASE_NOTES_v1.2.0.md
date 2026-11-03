# AWTRIX NG Control v1.2.0 — Text-to-Speech

## New
- `awtrix_ng_control.say` action: generate MP3 speech using a Home Assistant TTS engine and play it on AWTRIX NG using the device HTTP audio endpoint.
- Device selection through Home Assistant device picker (`device_id`) or existing MQTT prefix (`device`).
- Support for optional provider language, cache and options.
- Service field descriptions for the Home Assistant graphical action editor.

## Compatibility and validation
- Successfully tested on Ulanzi TC002 with `tts.edge_tts`.
- Google AI TTS playback has not yet been verified.
- AWTRIX 3 support remains available for Live Screen; this TTS service targets AWTRIX NG HTTP audio devices.
- Existing MQTT, Live Screen, HTTP controls, notifications, audio, backup and device-management source modules remain unchanged.

## Upgrade
Update through HACS or copy `custom_components/awtrix_ng_control` to the corresponding Home Assistant directory, then restart Home Assistant. Ensure an AWTRIX HTTP host is configured and a Home Assistant TTS entity is available.

## Notes
MP3 clip payloads must not exceed 2 MiB. This release preserves the existing integration configuration and does not change the MQTT topic prefixes.
