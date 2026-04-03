<h1 align="center">
 TOYA Decoder
</h1>

<p align="center">
  <a href="https://github.com/wielorzeczownik/ha-toya-decoder/actions/workflows/release.yml"><img src="https://img.shields.io/github/actions/workflow/status/wielorzeczownik/ha-toya-decoder/release.yml?branch=main&style=flat-square&label=build&labelColor=2d333b&color=2ea043" alt="Build Status"/></a>
  <img src="https://img.shields.io/github/actions/workflow/status/wielorzeczownik/ha-toya-decoder/release.yml?branch=main&nameFilter=hassfest&style=flat-square&label=Hassfest&labelColor=2d333b&color=2ea043" alt="Hassfest Status"/>
  <img src="https://img.shields.io/github/actions/workflow/status/wielorzeczownik/ha-toya-decoder/release.yml?branch=main&nameFilter=HACS&style=flat-square&label=HACS&labelColor=2d333b&color=2ea043" alt="HACS Validation Status"/>
  <a href="https://github.com/wielorzeczownik/ha-toya-decoder/releases/latest"><img src="https://img.shields.io/github/v/release/wielorzeczownik/ha-toya-decoder?style=flat-square&labelColor=2d333b&color=2ea043" alt="Latest Release"/></a>
  <a href="https://github.com/wielorzeczownik/ha-toya-decoder/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square&labelColor=2d333b" alt="License: MIT"/></a>
  <br/>
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square&logo=homeassistant&logoColor=white&labelColor=2d333b" alt="HACS Default"/></a>
  <a href="https://www.home-assistant.io/"><img src="https://img.shields.io/badge/Home%20Assistant-2024.6.0-41bdf5?style=flat-square&logo=homeassistant&logoColor=white&labelColor=2d333b" alt="Home Assistant"/></a>
</p>

<p align="center">
  <img
    src="https://raw.githubusercontent.com/wielorzeczownik/ha-toya-decoder/main/assets/toya-decoder.png"
    alt="TOYA Decoder Home Assistant Integration"
    width="260"
  >
</p>

<p align="center">🇬🇧 English | 🇵🇱 <a href="https://github.com/wielorzeczownik/ha-toya-decoder/blob/main/README.pl.md">Polski</a></p>

Control your **TOYA decoder** (set-top box) directly from **Home Assistant**. This custom integration exposes your TOYA cable TV decoder as a `media_player` entity, enabling full remote control, channel switching, and home automation - all from the Home Assistant UI or via automations.

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=wielorzeczownik&repository=ha-toya-decoder&category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open HACS Repository"/></a>
  <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=toya_decoder"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Add Integration" /></a>
</p>

## Features

- **Media player entity** per decoder - visible in the Home Assistant dashboard
- **Power control** - turn the TOYA decoder on and off via Home Assistant
- **Volume control** - volume up, volume down, and mute
- **Channel switching** - channel up/down, or jump directly to a channel number or name
- **Media browser** - browse the full TOYA channel list from the HA UI
- **`media_player.play_media` support** - automate channel changes in scripts and automations
- **Remote commands** - send any remote control key (play, pause, stop, back, OK, arrows, etc.)

## Installation via HACS

1. In Home Assistant, open **HACS → Integrations**.
2. Search for **TOYA Decoder** and install it.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for **TOYA Decoder**.
5. Enter your TOYA account credentials (the same login you use in the Toya GO app).

## Supported devices

This integration supports legacy TOYA decoders (non-Android TV) that return a non-empty `smartcard` value from the API. Android TV (ATV) devices return an empty smartcard and are not supported.

**Known legacy models (non-Android TV) - should be compatible:**

| Model                                             | Generation |
| ------------------------------------------------- | ---------- |
| Intek HD-C20CXM, HD-C20CXM Model S, HD-C20CXM PVR | 3G HD      |
| Intek HD-C63CX, HD-C64CXM                         | 3G HD      |
| Arion ARC-5510DR, ARC-5511DR                      | 3G HD      |
| Arion ARC-1010YR, ARC-1011YR, ARC-1013YR          | HD         |
| Intek C311CX                                      | SD         |

**Not supported (Android TV):** MAXX 4K (DTC974x, DTC974y, ARC-S110ZR), MAXX 4K IPTV (ARI-U110UR), TOYA 4K (UHD-C55CX).

> [!NOTE]
> Toya recently introduced 2FA for its customer portal. The Toya GO app API that this integration uses does not require 2FA, so enabling 2FA on your account does not affect this integration.

## Known limitations

- The API does not expose a direct "set channel" endpoint. Channel changes are implemented by emulating remote key presses (digit keys + navigation), so the result depends on the current on-screen UI state. In some screens the channel change must be confirmed with the Play button.
- Active standby is reported as ON by the API even when the decoder appears off.
- Passive standby is reported as OFF and the decoder cannot be powered on via the API.
- Channel number mapping issues in the API:
  - TVN HD is reported as channel 5 even though it is physically on channel 4.
  - Toya HD and Toya VOD are both reported as channel 6.

## Disclaimer

This is a community-made, unofficial integration not affiliated with TOYA. It may break if the backend API changes.
