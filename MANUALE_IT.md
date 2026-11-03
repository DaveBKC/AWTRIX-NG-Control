# AWTRIX NG Control 1.0.0 — Manuale italiano

## Ambito e stato dei test

Questa release mantiene i servizi della v0.6.9 e aggiunge il catalogo bilingue completo. I test statici NON dimostrano che ogni servizio funzioni sul TC002.

**Collaudati sul TC002 (segnalati dall’utente):**
- application selection
- Berry script setting read
- radio and audio status
- melody and MP3 operations (user reported)
- animated pushed app creation
- file_list on ICONS and PALETTES

**Non ancora collaudati sul TC002:**
- creation and inspection of a v0.6.9 or v1.0.0 backup
- media/script/settings restore
- file upload/download/delete
- Berry install/update/remove
- advanced notifications
- global overlays and transitions
- device_health and reboot
- per-app enabled state

## Installazione e aggiornamento

Copiare `custom_components/awtrix_ng_control` in `/config/custom_components/awtrix_ng_control`, riavviare Home Assistant, mantenere la configurazione esistente. Non eliminare e ricreare la voce di integrazione: potrebbe cambiare gli ID delle entità.

Le azioni sono in **Strumenti per sviluppatori → Azioni**. La lingua dei nomi delle azioni segue la lingua dell’interfaccia, mentre i loro identificativi restano sempre uguali.

## Principali percorsi locali

```text
/config/www/awtrix_icons/
/config/awtrix_ng_scripts/
/config/awtrix_ng_audio/
/config/awtrix_ng_files/<FOLDER>/
/config/awtrix_ng_downloads/<FOLDER>/
/config/awtrix_ng_backups/
```

## Catalogo dei servizi (70)

### Core, MQTT and notifications

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.notify` | Mostra notifica | `device`, `data` |
| `awtrix_ng_control.dismiss` | Chiudi notifica | `device` |
| `awtrix_ng_control.dismiss_named` | Chiudi notifica per nome | `device`, `name` |
| `awtrix_ng_control.settings` | Impostazioni | `device`, `data` |
| `awtrix_ng_control.push_app` | Pubblica app | `device`, `name`, `data` |
| `awtrix_ng_control.remove_app` | Rimuovi app | `device`, `name` |
| `awtrix_ng_control.switch_app` | Cambia app | `device`, `name` |
| `awtrix_ng_control.sound` | Suono | `device`, `data` |
| `awtrix_ng_control.rtttl` | Melodia RTTTL | `device`, `data` |
| `awtrix_ng_control.command` | Comando MQTT avanzato | `device`, `command`, `data`, `payload` |
| `awtrix_ng_control.http_request` | Invia richiesta HTTP avanzata al dispositivo | `device`, `method`, `path`, `data` |
| `awtrix_ng_control.notify_simple` | Notifica rapida | `device`, `message`, `duration`, `icon`, `color`, `sound` |
| `awtrix_ng_control.notification_advanced` | Notifica avanzata (HTTP) | `device`, `data` |
| `awtrix_ng_control.notification_dismiss_named_http` | Cancella notifica per nome (HTTP) | `device`, `name` |

### Applications and rotation

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.app_refresh` | Aggiorna applicazioni | `device` |
| `awtrix_ng_control.app_set_enabled` | Abilita o disabilita applicazione | `device`, `name`, `enabled` |
| `awtrix_ng_control.app_set_order` | Ordina applicazioni in rotazione | `device`, `order` |
| `awtrix_ng_control.app_list_http` | Elenca applicazioni (HTTP) | `device` |
| `awtrix_ng_control.app_show_http` | Mostra applicazione (HTTP) | `device`, `name`, `fast` |

### Radio and audio

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.radio_station` | Riproduce la stazione selezionata | `device`, `station` |
| `awtrix_ng_control.radio_stop` | Ferma la radio | `device` |
| `awtrix_ng_control.radio_refresh` | Aggiorna le stazioni dal dispositivo | `device` |
| `awtrix_ng_control.radio_add` | Aggiunge o aggiorna una stazione conservando le altre | `device`, `name`, `url` |
| `awtrix_ng_control.radio_remove` | Rimuove una stazione conservando le altre | `device`, `name` |
| `awtrix_ng_control.play_audio` | Riproduci oggetto audio | `device`, `data` |
| `awtrix_ng_control.stop_audio` | Interrompi gruppo audio | `device`, `data` |
| `awtrix_ng_control.audio_status` | Stato audio | `device` |
| `awtrix_ng_control.melody_list` | Elenco melodie | `device` |
| `awtrix_ng_control.melody_save` | Salva melodia RTTTL | `device`, `name`, `rtttl` |
| `awtrix_ng_control.melody_delete` | Elimina melodia | `device`, `name` |
| `awtrix_ng_control.mp3_list` | Elenco MP3 | `device` |
| `awtrix_ng_control.mp3_upload` | Carica MP3 | `device`, `filename` |
| `awtrix_ng_control.mp3_delete` | Elimina MP3 | `device`, `name` |
| `awtrix_ng_control.mp3_rename` | Rinomina MP3 | `device`, `old_name`, `new_name` |
| `awtrix_ng_control.audio_play_source` | Riproduci audio avanzato | `device`, `file`, `rtttl`, `song`, `speech`, `station`, `loop` |
| `awtrix_ng_control.audio_stop_group` | Ferma gruppo audio | `device`, `group` |

### Indicators, icons and files

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.indicator_set` | Imposta indicatore | `device`, `indicator`, `data` |
| `awtrix_ng_control.indicator_clear` | Spegni indicatore | `device`, `indicator` |
| `awtrix_ng_control.icon_list` | Elenca icone | `device` |
| `awtrix_ng_control.icon_upload` | Carica icona | `device`, `filename` |
| `awtrix_ng_control.icon_rename` | Rinomina icona | `device`, `old_name`, `new_name` |
| `awtrix_ng_control.icon_delete` | Elimina icona | `device`, `name` |
| `awtrix_ng_control.file_list` | Elenca file | `device`, `folder` |
| `awtrix_ng_control.file_upload` | Carica file | `device`, `folder`, `filename` |
| `awtrix_ng_control.file_download` | Scarica file | `device`, `folder`, `filename` |
| `awtrix_ng_control.file_delete` | Elimina file | `device`, `folder`, `filename` |

### Berry scripts

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.script_list` | Elenca script Berry | `device` |
| `awtrix_ng_control.script_read` | Leggi script Berry | `device`, `name` |
| `awtrix_ng_control.script_install` | Installa script Berry | `device`, `name`, `filename` |
| `awtrix_ng_control.script_update` | Aggiorna script Berry | `device`, `name`, `filename` |
| `awtrix_ng_control.script_remove` | Elimina script Berry | `device`, `name` |
| `awtrix_ng_control.script_config_get` | Leggi impostazioni script | `device`, `name` |
| `awtrix_ng_control.script_config_set` | Imposta parametri script | `device`, `name`, `settings` |

### Effects, display and diagnostics

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.device_info` | Informazioni dispositivo | `device` |
| `awtrix_ng_control.system_info` | Configurazione sistema | `device` |
| `awtrix_ng_control.device_logs` | Registri dispositivo | `device` |
| `awtrix_ng_control.device_capabilities` | Funzionalità dispositivo | `device` |
| `awtrix_ng_control.moodlight_set` | Imposta luce ambiente | `device`, `color`, `kelvin`, `brightness` |
| `awtrix_ng_control.moodlight_off` | Disattiva luce ambiente | `device` |
| `awtrix_ng_control.visual_capabilities` | Effetti grafici disponibili | `device` |
| `awtrix_ng_control.visual_effect_app` | Crea applicazione animata | `device`, `name`, `text`, `effect`, `effect_speed`, `palette`, `overlay`, `duration_ms`, `show_immediately`, `enable_rotation` |
| `awtrix_ng_control.visual_overlay_global` | Imposta effetto meteo globale | `device`, `overlay`, `speed`, `palette` |
| `awtrix_ng_control.visual_transition` | Imposta transizione tra applicazioni | `device`, `effect`, `duration_ms` |
| `awtrix_ng_control.device_health` | Diagnostica dispositivo | `device` |
| `awtrix_ng_control.device_reboot` | Riavvia dispositivo | `device`, `confirm` |

### Backup and selective restore

| Servizio | Funzione | Parametri |
|---|---|---|
| `awtrix_ng_control.backup_create` | Crea backup | `device`, `name`, `folders`, `settings`, `scripts` |
| `awtrix_ng_control.backup_inspect` | Verifica backup | `name` |
| `awtrix_ng_control.backup_restore_files` | Ripristina file multimediali | `device`, `name`, `folder`, `confirm` |
| `awtrix_ng_control.backup_restore_script` | Ripristina script Berry | `device`, `name`, `script`, `confirm`, `restore_options` |
| `awtrix_ng_control.backup_restore_settings` | Ripristina impostazioni display | `device`, `name`, `confirm` |

## Esempi pronti

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

Il backup dell’integrazione **non** è il backup nativo completo del firmware. Non include le credenziali Wi-Fi/MQTT né necessariamente tutti i dati interni degli script. I ripristini richiedono `confirm: true`; non testare su dati insostituibili. Eliminazione di file/script e riavvio sono operazioni reali. Conservare una copia del backup nativo prima di provare un ripristino.

Per i parametri obbligatori e le scelte ammesse consultare direttamente la descrizione dell’azione in Home Assistant: questo catalogo elenca tutti i nomi dei campi definiti, senza inventare valori predefiniti.

## Riferimento dettagliato dei campi

Questa sezione è derivata direttamente da `services.yaml`; «obbligatorio» riflette `required: true`, e gli esempi non sono valori predefiniti.

### `awtrix_ng_control.notify`

Invia un payload JSON AWTRIX NG sul display.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.dismiss`

Chiude la notifica attiva.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.dismiss_named`

Rimuove la notifica indicata.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.settings`

Applica le impostazioni del display.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.push_app`

Crea o aggiorna una app pushed.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.remove_app`

Elimina una app pushed.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.switch_app`

Mostra una app.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.sound`

Invia il payload per il comando sound.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.rtttl`

Invia il payload RTTTL.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.command`

Invia qualsiasi percorso di comando MQTT AWTRIX NG.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `command` | Sì | `text` | `—` |
| `data` | No | `object` | `—` |
| `payload` | No | `text` | `—` |

### `awtrix_ng_control.radio_station`

Riproduce la stazione selezionata

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `station` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_stop`

Ferma la radio

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_refresh`

Aggiorna le stazioni dal dispositivo

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_add`

Aggiunge o aggiorna una stazione conservando le altre

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `url` | Sì | `text` | `—` |

### `awtrix_ng_control.radio_remove`

Rimuove una stazione conservando le altre

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.play_audio`

Riproduci oggetto audio

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.stop_audio`

Interrompi gruppo audio

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.http_request`

Invia richiesta HTTP avanzata al dispositivo

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `method` | Sì | `select` | `—` |
| `path` | Sì | `text` | `—` |
| `data` | No | `object` | `—` |

### `awtrix_ng_control.notify_simple`

Mostra testo, icona, colore e suono senza scrivere JSON.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `message` | Sì | `text` | `—` |
| `duration` | No | `number` | `—` |
| `icon` | No | `text` | `—` |
| `color` | No | `text` | `—` |
| `sound` | No | `text` | `—` |

### `awtrix_ng_control.indicator_set`

Imposta uno dei tre LED indicatori con il payload JSON ufficiale.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `indicator` | Sì | `number` | `—` |
| `data` | Sì | `object` | `{True: True, 'color': '#00FF00'}` |

### `awtrix_ng_control.indicator_clear`

Spegne uno dei tre LED indicatori.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `indicator` | Sì | `number` | `—` |

### `awtrix_ng_control.app_refresh`

Rilegge le applicazioni e aggiorna il menu senza riavviare Home Assistant.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.app_set_enabled`

Modifica lo stato di una sola app senza alterare le altre.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `enabled` | Sì | `boolean` | `—` |

### `awtrix_ng_control.app_set_order`

Richiede tutte le app attualmente nella rotazione una sola volta; mantiene le app disabilitate.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `order` | Sì | `object` | `—` |

### `awtrix_ng_control.icon_list`

Restituisce l'elenco delle icone installate sul display e lo spazio utilizzato. Usa un'azione con risposta.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.icon_upload`

Carica una GIF/JPEG presente in /config/www/awtrix_icons sul dispositivo.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.icon_rename`

Rinomina un'icona esistente senza cambiare l'estensione.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `old_name` | Sì | `text` | `—` |
| `new_name` | Sì | `text` | `—` |

### `awtrix_ng_control.icon_delete`

Elimina definitivamente un'icona dal display.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.notification_advanced`

Invia una notifica completa, anche con layout a regioni e nome, validata dal firmware AWTRIX NG.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `data` | Sì | `object` | `—` |

### `awtrix_ng_control.notification_dismiss_named_http`

Rimuove una notifica identificata per nome, anche dalla coda.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_list`

Legge gli script installati e i relativi errori.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.script_read`

Restituisce il sorgente Berry installato.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_install`

Installa un nuovo script Berry da /config/awtrix_ng_scripts, senza sovrascrivere nomi esistenti.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.script_update`

Aggiorna uno script solo se il sorgente remoto non è cambiato (scriptUpdates).

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.script_remove`

ELIMINA lo script e i suoi dati persistenti; i file audio rimangono.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_config_get`

Legge i parametri configurabili Berry.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.script_config_set`

Modifica alcuni parametri, lasciando invariati gli altri.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `settings` | Sì | `object` | `—` |

### `awtrix_ng_control.audio_status`

Legge radio, alert e audio delle app (sola lettura).

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.melody_list`

Restituisce melodie RTTTL e relative informazioni (sola lettura).

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.melody_save`

Crea o sostituisce una melodia presente sul dispositivo.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `rtttl` | Sì | `text` | `—` |

### `awtrix_ng_control.melody_delete`

Elimina definitivamente la melodia specificata.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_list`

Legge file audio e suoni degli script (sola lettura).

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_upload`

Carica un MP3 precedentemente salvato in /config/awtrix_ng_audio/.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `filename` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_delete`

Elimina definitivamente un MP3 dalla cartella /MP3 del dispositivo.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |

### `awtrix_ng_control.mp3_rename`

Rinomina un MP3 senza cambiare i suoni propri degli script.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `old_name` | Sì | `text` | `—` |
| `new_name` | Sì | `text` | `—` |

### `awtrix_ng_control.audio_play_source`

Riproduce una sola sorgente fra file, RTTTL, song, speech e stazione.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `file` | No | `text` | `—` |
| `rtttl` | No | `text` | `—` |
| `song` | No | `text` | `—` |
| `speech` | No | `text` | `—` |
| `station` | No | `text` | `—` |
| `loop` | No | `boolean` | `—` |

### `awtrix_ng_control.audio_stop_group`

Ferma solo alert, suoni delle app o radio.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `group` | Sì | `select` | `—` |

### `awtrix_ng_control.device_info`

Read firmware version, memory, uptime and current app.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.system_info`

Read system settings from the AWTRIX device.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.device_logs`

Retrieve logs from the AWTRIX device.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.device_capabilities`

Read available effects, transitions, overlays, sensors and audio.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.moodlight_set`

Set full-screen ambient color, white temperature or brightness.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `color` | No | `text` | `'#FF5500'` |
| `kelvin` | No | `number` | `—` |
| `brightness` | No | `number` | `—` |

### `awtrix_ng_control.moodlight_off`

Disable ambient light and restore normal application display.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.visual_capabilities`

Read effects, transitions, overlays and palettes supported by this device.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.visual_effect_app`

Create or update a pushed app with animated background and optional overlay.

| Campo | Obbligatorio | Tipo | Esempio |
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

Show rain, snow or other weather animation over applications. Use none to turn off.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `overlay` | Sì | `text` | `'rain'` |
| `speed` | No | `number` | `0.5` |
| `palette` | No | `text` | `'Ocean'` |

### `awtrix_ng_control.visual_transition`

Select the animation and duration used between applications.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `effect` | Sì | `text` | `'Pixelate'` |
| `duration_ms` | Sì | `number` | `600` |

### `awtrix_ng_control.app_list_http`

Return all apps with enabled, present and rotation status.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.app_show_http`

Display an application immediately without changing global rotation settings.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'demo_fx'` |
| `fast` | No | `boolean` | `—` |

### `awtrix_ng_control.file_list`

List asset files and storage usage / Elenca i file e lo spazio utilizzato.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |

### `awtrix_ng_control.file_upload`

Upload from /config/awtrix_ng_files/FOLDER/filename.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |
| `filename` | Sì | `text` | `'ocean.txt'` |

### `awtrix_ng_control.file_download`

Save in /config/awtrix_ng_downloads/FOLDER/filename without overwriting.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |
| `filename` | Sì | `text` | `'ocean.txt'` |

### `awtrix_ng_control.file_delete`

Permanently delete one asset from AWTRIX / Elimina un file dal dispositivo.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `folder` | Sì | `select` | `—` |
| `filename` | Sì | `text` | `'ocean.txt'` |

### `awtrix_ng_control.backup_create`

Export supported media and optional non-secret settings and script sources to a verified local ZIP.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'tc002_backup_01'` |
| `folders` | No | `select` | `['ICONS', 'MELODIES', 'PALETTES', 'MP3']` |
| `settings` | No | `boolean` | `—` |
| `scripts` | No | `boolean` | `—` |

### `awtrix_ng_control.backup_inspect`

Validate ZIP checksums without changing the device.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `name` | Sì | `text` | `'tc002_backup_01'` |

### `awtrix_ng_control.backup_restore_files`

Restore only absent media files in one selected folder; never overwrite existing files.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `name` | Sì | `text` | `'tc002_backup_01'` |
| `folder` | Sì | `select` | `—` |
| `confirm` | Sì | `boolean` | `—` |

### `awtrix_ng_control.backup_restore_script`

Install a Berry script from an integration backup only if not present, optionally restoring saved options. No overwrites.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `script` | Sì | `text` | `—` |
| `confirm` | Sì | `boolean` | `—` |
| `restore_options` | No | `boolean` | `—` |

### `awtrix_ng_control.backup_restore_settings`

Restore approved display settings only. Excludes network, passwords, MQTT and system settings.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `—` |
| `name` | Sì | `text` | `—` |
| `confirm` | Sì | `boolean` | `—` |

### `awtrix_ng_control.device_health`

Read device state, display and network statistics without changing any setting. / Legge stato e diagnostica senza modifiche.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |

### `awtrix_ng_control.device_reboot`

Restart AWTRIX NG; explicit confirmation is required. / Riavvia AWTRIX NG con conferma obbligatoria.

| Campo | Obbligatorio | Tipo | Esempio |
|---|---|---|---|
| `device` | Sì | `text` | `'tc002'` |
| `confirm` | Sì | `boolean` | `—` |



## Live Screen (v1.1.6) — TC001 e TC002

La scheda Lovelace `custom:awtrix-live-screen-card` visualizza in tempo quasi reale il contenuto del display, con un aggiornamento MQTT al secondo solo mentre la scheda è aperta. Non utilizza entità camera né file PNG. Il TC001 può usare AWTRIX 3 firmware v0.98 e il TC002 AWTRIX NG. Entrambi sono stati collaudati su dispositivi reali.

Per attivarla, riavvia Home Assistant dopo l'installazione e registra in Dashboard → Modifica → Risorse una risorsa **Modulo JavaScript** con URL `/awtrix-ng-control/awtrix-live-screen.js` (senza parametri `?v=`). La prima apertura dopo un aggiornamento può richiedere la pulizia della cache del browser.

**TC002**
```yaml
type: custom:awtrix-live-screen-card
prefix: tc002
firmware: awtrix_ng
title: TC002 · Live Screen
```

**TC001**
```yaml
type: custom:awtrix-live-screen-card
prefix: PREFIX_MQTT_TC001
firmware: awtrix3
title: TC001 · Live Screen
```

Sostituisci `PREFIX_MQTT_TC001` con il prefisso MQTT reale del display. Gli utenti che visualizzano la scheda devono essere amministratori Home Assistant. Il rendering LED v1.1.6 è quello collaudato; la modifica v1.1.7 è stata scartata.

Per la diagnostica MQTT, AWTRIX 3 usa `<prefix>/sendscreen` e `<prefix>/screen`; AWTRIX NG usa `<prefix>/cmd/screen/get` e `<prefix>/state/screen`.

## Sintesi vocale TTS (v1.2.0)

L'azione `awtrix_ng_control.say` genera un MP3 tramite un'entità TTS già configurata in Home Assistant e lo invia direttamente al dispositivo **AWTRIX NG** tramite HTTP. Verificata sul TC002 con `tts.edge_tts`; il motore Google AI TTS non è ancora stato verificato sul dispositivo. Live Screen per AWTRIX 3 rimane invariato: il TTS qui descritto è destinato ai dispositivi AWTRIX NG con API HTTP.

Nell'editor puoi scegliere il dispositivo Home Assistant (`device_id`) **oppure** il prefisso MQTT (`device`, per esempio `tc002`), non entrambi. Serve l'indirizzo HTTP del display configurato e raggiungibile.

```yaml
action: awtrix_ng_control.say
data:
  device: tc002
  engine: tts.edge_tts
  message: "La batteria Bluetti è completamente carica."
```

Opzioni aggiuntive: `language`, `cache`, `options`. Limite MP3: 2 MiB. I nomi dei motori TTS dipendono dalle entità presenti in Home Assistant.
