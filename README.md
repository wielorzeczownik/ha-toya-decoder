<h1 align="center">
 TOYA Decoder
</h1>

<p align="center">
  <a href="https://hacs.xyz/">
    <picture>
      <source
        media="(prefers-color-scheme: dark)"
        srcset="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square&logo=homeassistant&logoColor=white&labelColor=2d333b"
      >
      <source
        media="(prefers-color-scheme: light)"
        srcset="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square&logo=homeassistant&logoColor=white"
      >
      <img
        src="https://img.shields.io/badge/HACS-Custom-orange?style=flat-square&logo=homeassistant&logoColor=white"
        alt="HACS Custom"
      />
    </picture>
  </a>
  <a href="https://www.home-assistant.io/">
    <picture>
      <source
        media="(prefers-color-scheme: dark)"
        srcset="https://img.shields.io/badge/Home%20Assistant-2026.10.0-41bdf5?style=flat-square&logo=homeassistant&logoColor=white&labelColor=2d333b"
      >
      <source
        media="(prefers-color-scheme: light)"
        srcset="https://img.shields.io/badge/Home%20Assistant-2026.10.0-41bdf5?style=flat-square&logo=homeassistant&logoColor=white"
      >
      <img
        src="https://img.shields.io/badge/Home%20Assistant-2026.10.0-41bdf5?style=flat-square&logo=homeassistant&logoColor=white"
        alt="Home Assistant"
      />
    </picture>
  </a>
  <a href="LICENSE">
    <picture>
      <source
        media="(prefers-color-scheme: dark)"
        srcset="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square&labelColor=2d333b"
      >
      <source
        media="(prefers-color-scheme: light)"
        srcset="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square"
      >
      <img
        src="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square"
        alt="License: MIT"
      />
    </picture>
  </a>
</p>

Home Assistant custom integration for legacy TOYA decoders (non-Android TV).
It uses an unofficial API based on decompilation of an older Toya GO app.

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

1. HACS -> Integrations -> Custom repositories -> Add this repo (type: Integration).
2. Install "TOYA Decoder (Legacy)" from HACS.
3. Restart Home Assistant.
4. Settings -> Devices & Services -> Add Integration -> "TOYA Decoder (Legacy)".

## Installation (manual)

1. Copy `custom_components/toya_decoder` into your HA config directory:
   `<config>/custom_components/toya_decoder`
2. Restart Home Assistant.
3. Settings -> Devices & Services -> Add Integration -> "TOYA Decoder (Legacy)".

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
