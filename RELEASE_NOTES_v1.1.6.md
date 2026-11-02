# AWTRIX NG Control v1.1.6 — Live Screen

## English

### Added
- Lovelace Live Screen card for **AWTRIX NG** (TC002, 52×16) and **AWTRIX 3** (TC001, 32×8; tested on firmware 0.98).
- MQTT/WebSocket-based display mirroring, approximately one frame per second, while the card is visible.
- Device-style bezel, compact heading, LIVE indicator, and sharper per-LED rendering with dark gutters.
- Shared polling when multiple viewers are watching the same display.

### Setup
Register the JavaScript module resource `/awtrix-ng-control/awtrix-live-screen.js` (no query suffix) and add a manual `custom:awtrix-live-screen-card` using the correct MQTT prefix and firmware option. See `README.md`, `MANUALE_EN.md`, and `LIVE_SCREEN_IT_EN.md`.

### Compatibility
Existing HTTP/MQTT controls and native advanced notifications are preserved. Live Screen has been verified on both TC001 and TC002. Some other advanced services still need additional validation.

## Italiano

### Novità
- Scheda Lovelace Live Screen per **AWTRIX NG** (TC002, 52×16) e **AWTRIX 3** (TC001, 32×8; firmware 0.98 collaudato).
- Mirroring tramite MQTT/WebSocket, circa un fotogramma al secondo quando la scheda è visualizzata.
- Cornice grafica tipo dispositivo, intestazione compatta, indicatore LIVE e rendering LED separati.
- Polling condiviso fra più utenti che osservano lo stesso dispositivo.

### Configurazione
Aggiungere la risorsa JavaScript `/awtrix-ng-control/awtrix-live-screen.js`, senza suffissi, e la scheda `custom:awtrix-live-screen-card` con il prefisso MQTT effettivo. Consultare `MANUALE_IT.md` e `LIVE_SCREEN_IT_EN.md`.

### Compatibilità
I controlli già presenti rimangono invariati. Live Screen è stato verificato su TC001 e TC002; altri servizi avanzati richiedono ulteriori collaudi.
