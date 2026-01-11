<h1 align="center">
 TOYA Decoder
</h1>

<p align="center">
  <a href="https://hacs.xyz/">
    <img
      src="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square&logo=homeassistant&logoColor=white"
      alt="HACS Custom"
    />
  </a>
  <a href="https://www.home-assistant.io/">
    <img
      src="https://img.shields.io/badge/Home%20Assistant-2026.1.0-41bdf5?style=flat-square&logo=homeassistant&logoColor=white"
      alt="Home Assistant"
    />
  </a>
  <a href="LICENSE">
    <img
      src="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square"
      alt="License: MIT"
    />
  </a>
</p>

<p align="center">
  <img
    src="https://raw.githubusercontent.com/wielorzeczownik/ha-toya-decoder/main/assets/toya-decoder.png"
    alt="TOYA Decoder"
    width="260"
  >
</p>

Home Assistant custom integration for legacy TOYA decoders (non-Android TV).
It uses an unofficial API based on decompilation of an older [Toya GO](https://play.google.com/store/apps/details?id=com.toya.toyago&hl=pl) app.

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=wielorzeczownik&repository=ha-toya-decoder&category=integration">
    <img
      src="https://my.home-assistant.io/badges/hacs_repository.svg"
      alt="Open HACS Repository"
    />
  </a>
  <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=toya_decoder">
    <img
      src="https://my.home-assistant.io/badges/config_flow_start.svg"
      alt="Add Integration"
    />
  </a>
</p>

## What it provides

- A `media_player` entity per decoder.
- Standard media player controls in the HA UI: power toggle, volume up/down,
  mute, play/pause, stop, and channel up/down.
- Media browser with a channel list and `media_player.play_media` support
  (by channel number or label).

## Supported devices

This integration only supports decoders that return a non-empty `smartcard`
value from the API. Android TV (ATV) devices return an empty string and are
not supported, so they will not work with this integration.

## Installation (HACS)

1. HACS -> Integrations -> Search for "TOYA Decoder" and install it.
2. Restart Home Assistant.
3. Settings -> Devices & Services -> Add Integration -> "TOYA Decoder".

## Known limitations and issues

- The API does not expose a direct "set channel" endpoint. Channel changes are
  implemented by emulating remote key presses (digits and navigation), so the
  behavior depends on the on-screen UI state. In some screens the channel change
  must be confirmed with the Play button (which behaves like OK in that frame).
- Active standby is reported as ON by the API even when the device looks off.
- Passive standby is reported as OFF and the device cannot be powered on via API.
- Channel mapping issues reported by the API:
  - TVN HD is reported as channel 5 even though it is actually on 4.
  - Toya HD and Toya VOD are both reported as channel 6.

## Disclaimer

This project is community-made, unofficial, and may break if the backend API
changes.
