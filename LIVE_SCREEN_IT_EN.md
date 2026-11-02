# Live Screen v1.1.6 / Schermo in diretta


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


## Live Screen (v1.1.6) — TC001 and TC002

The `custom:awtrix-live-screen-card` Lovelace card mirrors the physical display via MQTT and Home Assistant WebSocket at approximately one frame per second while a viewer has the card open. No camera entity or PNG file is required. It supports TC001 running AWTRIX 3 firmware v0.98 and TC002 running AWTRIX NG. Both have been tested on physical devices.

After installing the integration, restart Home Assistant and add the JavaScript **module** resource `/awtrix-ng-control/awtrix-live-screen.js` under Dashboard → Edit → Resources. No `?v=` suffix is required. Reload your browser or clear its cache after upgrading if you still see the old renderer.

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
prefix: YOUR_TC001_MQTT_PREFIX
firmware: awtrix3
title: TC001 · Live Screen
```

Use the actual TC001 MQTT prefix. Viewing requires a Home Assistant administrator account. Version 1.1.6 uses the tested LED renderer; the 1.1.7 renderer change was rejected. AWTRIX 3 uses `<prefix>/sendscreen` and `<prefix>/screen`; AWTRIX NG uses `<prefix>/cmd/screen/get` and `<prefix>/state/screen`.
