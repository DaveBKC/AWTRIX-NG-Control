# AWTRIX NG Control 1.0.0 — English user guide

## Scope and testing status

This release retains v0.6.9 services and adds a full bilingual service catalog. Static checks DO NOT prove that every operation works on the TC002.

**Confirmed on the TC002 (reported by the user):**
- application selection
- Berry script setting read
- radio and audio status
- melody and MP3 operations (user reported)
- animated pushed app creation
- file_list on ICONS and PALETTES

**Not yet tested on the TC002:**
- creation and inspection of a v0.6.9 or v1.0.0 backup
- media/script/settings restore
- file upload/download/delete
- Berry install/update/remove
- advanced notifications
- global overlays and transitions
- device_health and reboot
- per-app enabled state

## Installation and update

Copy `custom_components/awtrix_ng_control` to `/config/custom_components/awtrix_ng_control`, restart Home Assistant, and keep the existing integration entry. Do not remove and recreate it: entity IDs may change.

Actions appear under **Developer Tools → Actions**. Action labels are localized; service IDs remain unchanged.

## Main local paths

```text
/config/www/awtrix_icons/
/config/awtrix_ng_scripts/
/config/awtrix_ng_audio/
/config/awtrix_ng_files/<FOLDER>/
/config/awtrix_ng_downloads/<FOLDER>/
/config/awtrix_ng_backups/
```

## Service catalog (70)

### Core, MQTT and notifications

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.notify` | Send notification | `device`, `data` |
| `awtrix_ng_control.dismiss` | Dismiss notification | `device` |
| `awtrix_ng_control.dismiss_named` | Dismiss notification by name | `device`, `name` |
| `awtrix_ng_control.settings` | Change display settings | `device`, `data` |
| `awtrix_ng_control.push_app` | Publish application | `device`, `name`, `data` |
| `awtrix_ng_control.remove_app` | Remove application | `device`, `name` |
| `awtrix_ng_control.switch_app` | Show application | `device`, `name` |
| `awtrix_ng_control.sound` | Play sound | `device`, `data` |
| `awtrix_ng_control.rtttl` | Play RTTTL melody | `device`, `data` |
| `awtrix_ng_control.command` | Advanced MQTT command | `device`, `command`, `data`, `payload` |
| `awtrix_ng_control.http_request` | Advanced HTTP request | `device`, `method`, `path`, `data` |
| `awtrix_ng_control.notify_simple` | Quick notification | `device`, `message`, `duration`, `icon`, `color`, `sound` |
| `awtrix_ng_control.notification_advanced` | Advanced notification (HTTP) | `device`, `data` |
| `awtrix_ng_control.notification_dismiss_named_http` | Dismiss named notification (HTTP) | `device`, `name` |

### Applications and rotation

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.app_refresh` | Refresh applications | `device` |
| `awtrix_ng_control.app_set_enabled` | Enable or disable application | `device`, `name`, `enabled` |
| `awtrix_ng_control.app_set_order` | Set application rotation order | `device`, `order` |
| `awtrix_ng_control.app_list_http` | List applications (HTTP) | `device` |
| `awtrix_ng_control.app_show_http` | Show application (HTTP) | `device`, `name`, `fast` |

### Radio and audio

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.radio_station` | Play selected radio station | `device`, `station` |
| `awtrix_ng_control.radio_stop` | Stop radio | `device` |
| `awtrix_ng_control.radio_refresh` | Refresh radio stations | `device` |
| `awtrix_ng_control.radio_add` | Add or update radio station | `device`, `name`, `url` |
| `awtrix_ng_control.radio_remove` | Remove radio station | `device`, `name` |
| `awtrix_ng_control.play_audio` | Play audio | `device`, `data` |
| `awtrix_ng_control.stop_audio` | Stop audio group | `device`, `data` |
| `awtrix_ng_control.audio_status` | Audio status | `device` |
| `awtrix_ng_control.melody_list` | List melodies | `device` |
| `awtrix_ng_control.melody_save` | Save RTTTL melody | `device`, `name`, `rtttl` |
| `awtrix_ng_control.melody_delete` | Delete melody | `device`, `name` |
| `awtrix_ng_control.mp3_list` | List MP3 files | `device` |
| `awtrix_ng_control.mp3_upload` | Upload MP3 | `device`, `filename` |
| `awtrix_ng_control.mp3_delete` | Delete MP3 | `device`, `name` |
| `awtrix_ng_control.mp3_rename` | Rename MP3 | `device`, `old_name`, `new_name` |
| `awtrix_ng_control.audio_play_source` | Play advanced audio source | `device`, `file`, `rtttl`, `song`, `speech`, `station`, `loop` |
| `awtrix_ng_control.audio_stop_group` | Stop audio group | `device`, `group` |

### Indicators, icons and files

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.indicator_set` | Set indicator | `device`, `indicator`, `data` |
| `awtrix_ng_control.indicator_clear` | Clear indicator | `device`, `indicator` |
| `awtrix_ng_control.icon_list` | List icons | `device` |
| `awtrix_ng_control.icon_upload` | Upload icon | `device`, `filename` |
| `awtrix_ng_control.icon_rename` | Rename icon | `device`, `old_name`, `new_name` |
| `awtrix_ng_control.icon_delete` | Delete icon | `device`, `name` |
| `awtrix_ng_control.file_list` | List files | `device`, `folder` |
| `awtrix_ng_control.file_upload` | Upload file | `device`, `folder`, `filename` |
| `awtrix_ng_control.file_download` | Download file | `device`, `folder`, `filename` |
| `awtrix_ng_control.file_delete` | Delete file | `device`, `folder`, `filename` |

### Berry scripts

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.script_list` | List Berry scripts | `device` |
| `awtrix_ng_control.script_read` | Read Berry script | `device`, `name` |
| `awtrix_ng_control.script_install` | Install Berry script | `device`, `name`, `filename` |
| `awtrix_ng_control.script_update` | Update Berry script | `device`, `name`, `filename` |
| `awtrix_ng_control.script_remove` | Remove Berry script | `device`, `name` |
| `awtrix_ng_control.script_config_get` | Read script settings | `device`, `name` |
| `awtrix_ng_control.script_config_set` | Update script settings | `device`, `name`, `settings` |

### Effects, display and diagnostics

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.device_info` | Device information | `device` |
| `awtrix_ng_control.system_info` | System settings | `device` |
| `awtrix_ng_control.device_logs` | Device logs | `device` |
| `awtrix_ng_control.device_capabilities` | Device capabilities | `device` |
| `awtrix_ng_control.moodlight_set` | Set ambient light | `device`, `color`, `kelvin`, `brightness` |
| `awtrix_ng_control.moodlight_off` | Disable ambient light | `device` |
| `awtrix_ng_control.visual_capabilities` | Visual effects available | `device` |
| `awtrix_ng_control.visual_effect_app` | Create animated application | `device`, `name`, `text`, `effect`, `effect_speed`, `palette`, `overlay`, `duration_ms`, `show_immediately`, `enable_rotation` |
| `awtrix_ng_control.visual_overlay_global` | Set global weather overlay | `device`, `overlay`, `speed`, `palette` |
| `awtrix_ng_control.visual_transition` | Set application transition | `device`, `effect`, `duration_ms` |
| `awtrix_ng_control.device_health` | Device diagnostics | `device` |
| `awtrix_ng_control.device_reboot` | Restart device | `device`, `confirm` |

### Backup and selective restore

| Service | Purpose | Parameters |
|---|---|---|
| `awtrix_ng_control.backup_create` | Create backup | `device`, `name`, `folders`, `settings`, `scripts` |
| `awtrix_ng_control.backup_inspect` | Inspect backup | `name` |
| `awtrix_ng_control.backup_restore_files` | Restore media files | `device`, `name`, `folder`, `confirm` |
| `awtrix_ng_control.backup_restore_script` | Restore Berry script | `device`, `name`, `script`, `confirm`, `restore_options` |
| `awtrix_ng_control.backup_restore_settings` | Restore display settings | `device`, `name`, `confirm` |

## Ready-to-use examples

### Leggere le applicazioni / List applications
```yaml
action: awtrix_ng_control.app_list_http
data:
  device: tc002
```

### Mostrare subito un effetto / Show an effect immediately
```yaml
action: awtrix_ng_control.visual_effect_app
data:
  device: tc002
  name: demo_fx
  text: CIAO
  effect: Pacifica
  effect_speed: 0.5
  palette: Ocean
  show_immediately: true
  enable_rotation: false
```

### Leggere le opzioni Berry / Read Berry settings
```yaml
action: awtrix_ng_control.script_config_get
data:
  device: tc002
  name: Beautiful-Weather
```

### Cambio pagina automatico / Automatic page switching
```yaml
action: awtrix_ng_control.script_config_set
data:
  device: tc002
  name: Beautiful-Weather
  settings:
    mode: auto
```

### Stato audio / Audio status
```yaml
action: awtrix_ng_control.audio_status
data:
  device: tc002
```

### File installati / Device files
```yaml
action: awtrix_ng_control.file_list
data:
  device: tc002
  folder: ICONS
```

### Backup selettivo / Integration backup
```yaml
action: awtrix_ng_control.backup_create
data:
  device: tc002
  name: tc002_pre_v100
```

```yaml
action: awtrix_ng_control.backup_inspect
data:
  name: tc002_pre_v100
```

## Precauzioni / Precautions

The integration backup is **not** the firmware’s full native backup. It excludes Wi-Fi/MQTT credentials and may omit internal script data. Restore actions require `confirm: true`; do not test on irreplaceable data. File/script deletion and restart are real operations. Keep a native backup before testing restores.

For required fields and allowed values, check the action description in Home Assistant. This catalog lists actual declared field names without inventing defaults.

## Detailed field reference

This section is generated directly from `services.yaml`; “required” reflects `required: true`, and examples are not default values.

### `awtrix_ng_control.notify`

AWTRIX NG action: send notification.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.dismiss`

AWTRIX NG action: dismiss notification.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.dismiss_named`

AWTRIX NG action: dismiss notification by name.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.settings`

AWTRIX NG action: change display settings.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.push_app`

AWTRIX NG action: publish application.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.remove_app`

AWTRIX NG action: remove application.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.switch_app`

AWTRIX NG action: show application.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.sound`

AWTRIX NG action: play sound.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.rtttl`

AWTRIX NG action: play rtttl melody.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.command`

AWTRIX NG action: advanced mqtt command.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `command` | Sì | `text` | `—` |
| `data` | No | `object` | `—` |
| `payload` | No | `text` | `—` |

### `awtrix_ng_control.radio_station`

AWTRIX NG action: play selected radio station.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `station` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_stop`

AWTRIX NG action: stop radio.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_refresh`

AWTRIX NG action: refresh radio stations.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_add`

AWTRIX NG action: add or update radio station.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `url` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_remove`

AWTRIX NG action: remove radio station.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.play_audio`

AWTRIX NG action: play audio.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.stop_audio`

AWTRIX NG action: stop audio group.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.http_request`

AWTRIX NG action: advanced http request.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `method` | Sì | `select` | `—` |
| `path` | Sì | `text` | `—` |
| `data` | No | `object` | `—` |

### `awtrix_ng_control.notify_simple`

AWTRIX NG action: quick notification.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `message` | Sì | `text` | `—` |
| `duration` | No | `number` | `—` |
| `icon` | No | `text` | `—` |
| `color` | No | `text` | `—` |
| `sound` | No | `text` | `—` |

### `awtrix_ng_control.indicator_set`

AWTRIX NG action: set indicator.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `indicator` | Sì | `number` | `—` |
| `data` | Sì | `object` | `{True: True, 'color': '#00FF00'}` |

### `awtrix_ng_control.indicator_clear`

AWTRIX NG action: clear indicator.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `indicator` | Sì | `number` | `—` |

### `awtrix_ng_control.app_refresh`

AWTRIX NG action: refresh applications.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.app_set_enabled`

Enable or disable one app without changing the rotation order.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `enabled` | Sì | `boolean` | `—` |

### `awtrix_ng_control.app_set_order`

AWTRIX NG action: set application rotation order.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `order` | Sì | `object` | `—` |

### `awtrix_ng_control.icon_list`

AWTRIX NG action: list icons.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.icon_upload`

AWTRIX NG action: upload icon.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.icon_rename`

AWTRIX NG action: rename icon.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `old_name` | Sì | `text` | `—` |
| `new_name` | Sì | `text` | `—` |

### `awtrix_ng_control.icon_delete`

AWTRIX NG action: delete icon.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.notification_advanced`

AWTRIX NG action: advanced notification (http).

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.notification_dismiss_named_http`

AWTRIX NG action: dismiss named notification (http).

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_list`

AWTRIX NG action: list berry scripts.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.script_read`

AWTRIX NG action: read berry script.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_install`

AWTRIX NG action: install berry script.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.script_update`

AWTRIX NG action: update berry script.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.script_remove`

Remove a Berry script and its persistent data. This operation is destructive.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_config_get`

AWTRIX NG action: read script settings.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_config_set`

AWTRIX NG action: update script settings.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `settings` | Sì | `object` | `—` |

### `awtrix_ng_control.audio_status`

AWTRIX NG action: audio status.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.melody_list`

AWTRIX NG action: list melodies.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.melody_save`

AWTRIX NG action: save rtttl melody.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `rtttl` | Sì | `text` | `—` |

### `awtrix_ng_control.melody_delete`

AWTRIX NG action: delete melody.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_list`

AWTRIX NG action: list mp3 files.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_upload`

AWTRIX NG action: upload mp3.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_delete`

AWTRIX NG action: delete mp3.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_rename`

AWTRIX NG action: rename mp3.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `old_name` | Sì | `text` | `—` |
| `new_name` | Sì | `text` | `—` |

### `awtrix_ng_control.audio_play_source`

AWTRIX NG action: play advanced audio source.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `file` | No | `text` | `—` |
| `rtttl` | No | `text` | `—` |
| `song` | No | `text` | `—` |
| `speech` | No | `text` | `—` |
| `station` | No | `text` | `—` |
| `loop` | No | `boolean` | `—` |

### `awtrix_ng_control.audio_stop_group`

AWTRIX NG action: stop audio group.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `group` | Sì | `select` | `—` |

### `awtrix_ng_control.device_info`

Read firmware version, memory, uptime and current app.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.system_info`

Read system settings from the AWTRIX device.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.device_logs`

Retrieve logs from the AWTRIX device.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.device_capabilities`

Read available effects, transitions, overlays, sensors and audio.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.moodlight_set`

Set full-screen ambient color, white temperature or brightness.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `color` | No | `text` | `'#FF5500'` |
| `kelvin` | No | `number` | `—` |
| `brightness` | No | `number` | `—` |

### `awtrix_ng_control.moodlight_off`

Disable ambient light and restore normal application display.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.visual_capabilities`

AWTRIX NG action: visual effects available.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.visual_effect_app`

Create or update an animated pushed app; optionally show it immediately or enable rotation.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'demo_fx'` |
| `text` | Sì | `text` | `'HELLO'` |
| `effect` | No | `text` | `'Pacifica'` |
| `effect_speed` | No | `number` | `0.5` |
| `palette` | No | `text` | `'Ocean'` |
| `overlay` | No | `text` | `'snow'` |
| `duration_ms` | No | `number` | `7000` |
| `show_immediately` | No | `boolean` | `—` |
| `enable_rotation` | No | `boolean` | `—` |

### `awtrix_ng_control.visual_overlay_global`

AWTRIX NG action: set global weather overlay.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `overlay` | Sì | `text` | `'rain'` |
| `speed` | No | `number` | `0.5` |
| `palette` | No | `text` | `'Ocean'` |

### `awtrix_ng_control.visual_transition`

AWTRIX NG action: set application transition.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `effect` | Sì | `text` | `'Pixelate'` |
| `duration_ms` | Sì | `number` | `600` |

### `awtrix_ng_control.app_list_http`

List applications and their states

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.app_show_http`

Show an application immediately

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'demo_fx'` |
| `fast` | No | `boolean` | `—` |

### `awtrix_ng_control.file_list`

List asset files

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |

### `awtrix_ng_control.file_upload`

Upload an asset file

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |
| `filename` | Sì | `text` | `'ocean.txt'` |

### `awtrix_ng_control.file_download`

Download an asset file

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |
| `filename` | Sì | `text` | `'ocean.txt'` |

### `awtrix_ng_control.file_delete`

Permanently delete one file from a supported media folder.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |
| `filename` | Sì | `text` | `'ocean.txt'` |

### `awtrix_ng_control.backup_create`

Create an integration-specific backup of the supported data (not a full firmware backup).

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'tc002_backup_01'` |
| `folders` | No | `select` | `['ICONS', 'MELODIES', 'PALETTES', 'MP3']` |
| `settings` | No | `boolean` | `—` |
| `scripts` | No | `boolean` | `—` |

### `awtrix_ng_control.backup_inspect`

Inspect and validate an integration backup without changing the device.

| Field | Required | Type | Example |
|---|---|---|---|
| `name` | Sì | `text` | `'tc002_backup_01'` |

### `awtrix_ng_control.backup_restore_files`

Restore files selectively. Requires confirmation and refuses existing filenames.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'tc002_backup_01'` |
| `folder` | Sì | `select` | `—` |
| `confirm` | Sì | `boolean` | `—` |

### `awtrix_ng_control.backup_restore_script`

Restore a missing Berry script and optionally its saved options. Requires confirmation.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `script` | Sì | `text` | `—` |
| `confirm` | Sì | `boolean` | `—` |
| `restore_options` | No | `boolean` | `—` |

### `awtrix_ng_control.backup_restore_settings`

Restore supported display settings, excluding Wi-Fi, MQTT and credentials. Requires confirmation.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `confirm` | Sì | `boolean` | `—` |

### `awtrix_ng_control.device_health`

Read firmware, Wi-Fi signal and uptime without changing settings.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.device_reboot`

Restart the display. Explicit confirmation is required.

| Field | Required | Type | Example |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `confirm` | Sì | `boolean` | `—` |

