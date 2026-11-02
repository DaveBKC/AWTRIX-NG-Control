# \# AWTRIX NG Control

# 

# \*\*Advanced Home Assistant Custom Integration for AWTRIX NG\*\*

# 

# AWTRIX NG Control is a custom Home Assistant integration designed to provide centralized control and management of AWTRIX NG devices.

# 

# Developed primarily for the \*\*Ulanzi TC002\*\*, it combines HTTP API and MQTT functionality to manage applications, notifications, visual effects, Berry scripts, audio, multimedia files, backups and device maintenance.

# 

# \*\*Version:\*\* 1.0.1  

# \*\*Languages:\*\* English and Italian  

# \*\*Installation:\*\* HACS or manual

# 

# \## Features

# 

# \### Display and Applications

# \- Display power and brightness

# \- Clock face selection

# \- Automatic application rotation

# \- Application selection, activation and individual enable/disable controls

# \- RGB indicators

# \- Transition effects and duration settings

# 

# \### Notifications

# \- Standard and advanced notifications

# \- Custom multi-region layouts

# \- Text, colors, icons, sounds and scrolling

# \- Notification duration and stacking

# \- Dismiss notifications by name

# 

# \### Visual Effects

# \- Animated backgrounds

# \- Effects and color palettes

# \- Weather-style overlays

# \- Application transition animations

# \- Immediate display of newly created applications

# 

# \### Berry Scripts

# \- List and inspect installed scripts

# \- Install, update and remove scripts

# \- Read and modify script configuration

# \- Export and restore supported script settings

# 

# \### Audio and Internet Radio

# \- Radio station selection and playback controls

# \- Audio status and diagnostics

# \- MP3 management

# \- RTTTL melodies

# \- Audio volume and playback control

# 

# \### File Management

# \- Browse device files

# \- Upload and download supported multimedia files

# \- Delete files

# \- Manage icons, MP3s, palettes and melodies

# \- Monitor storage usage

# 

# \### Backup, Restore and Maintenance

# \- Create and inspect backup archives

# \- Verify archive integrity

# \- Selectively restore supported files, scripts and settings

# \- Device health and system diagnostics

# \- Controlled reboot

# 

# \*\*Note:\*\* The integration's selective backup is not a replacement for the firmware's native full backup.

# 

# \## Installation via HACS

# 

# 1\. Open \*\*HACS\*\* in Home Assistant.

# 2\. Open the menu and select \*\*Custom repositories\*\*.

# 3\. Add the following repository:

# 

# &#x20;  `https://github.com/LinusIta/AWTRIX-NG-Control`

# 

# 4\. Select \*\*Integration\*\* as the repository type.

# 5\. Find \*\*AWTRIX NG Control\*\* and select \*\*Download\*\*.

# 6\. Restart Home Assistant.

# 7\. Open \*\*Settings → Devices \& Services → Add Integration\*\*.

# 8\. Search for \*\*AWTRIX NG Control\*\* and follow the configuration flow.

# 

# An existing configuration entry should be preserved when upgrading.

# 

# \## Manual Installation

# 

# Copy the directory:

# 

# `custom\_components/awtrix\_ng\_control`

# 

# into your Home Assistant configuration directory:

# 

# `/config/custom\_components/awtrix\_ng\_control`

# 

# Restart Home Assistant and add the integration through \*\*Settings → Devices \& Services\*\*.

# 

# \## Usage Example

# 

# List applications installed on the device:

# 

# ```yaml

# action: awtrix\_ng\_control.app\_list\_http

# data:

# &#x20; device: tc002

# ```

# 

# Display an application immediately:

# 

# ```yaml

# action: awtrix\_ng\_control.app\_show\_http

# data:

# &#x20; device: tc002

# &#x20; name: Beautiful-Weather

# &#x20; fast: true

# ```

# 

# Retrieve Berry script configuration:

# 

# ```yaml

# action: awtrix\_ng\_control.script\_config\_get

# data:

# &#x20; device: tc002

# &#x20; name: Beautiful-Weather

# ```

# 

# \## Documentation

# 

# \- \[Manuale completo in italiano](MANUALE\_IT.md)

# \- \[Full English User Guide](MANUALE\_EN.md)

# 

# Both guides include available actions, configuration parameters and YAML examples.

# 

# \## Compatibility

# 

# Developed primarily for \*\*Ulanzi TC002 running AWTRIX NG\*\*.

# 

# Compatibility with other AWTRIX NG devices and firmware versions may vary.

# 

# \## Development and Testing Status

# 

# This is a feature-complete initial release. Core features have been tested on an Ulanzi TC002, including application selection, Berry script configuration retrieval, audio diagnostics, visual application creation and file listing.

# 

# Some advanced operations, particularly backup restoration, file modification and device maintenance, still require additional validation on physical hardware.

# 

# \*\*Use destructive actions and restore operations with care.\*\*

# 

# \## Feedback and Contributions

# 

# Bug reports, feature requests and contributions are welcome through \[GitHub Issues](https://github.com/LinusIta/AWTRIX-NG-Control/issues).

# 

# This project was developed with the assistance of ChatGPT.

# 

# \## Acknowledgements

# 

# Thanks to the AWTRIX NG developers for creating the firmware and providing the APIs that make this integration possible.

