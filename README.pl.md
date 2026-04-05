<h1 align="center">
 TOYA Decoder
</h1>

<p align="center">
  <a href="https://github.com/wielorzeczownik/ha-toya-decoder/actions/workflows/release.yml"><img src="https://img.shields.io/github/actions/workflow/status/wielorzeczownik/ha-toya-decoder/release.yml?branch=main&style=flat-square&label=build&labelColor=2d333b&color=2ea043" alt="Status buildu"/></a>
  <img src="https://img.shields.io/github/actions/workflow/status/wielorzeczownik/ha-toya-decoder/release.yml?branch=main&nameFilter=hassfest&style=flat-square&label=Hassfest&labelColor=2d333b&color=2ea043" alt="Hassfest Status"/>
  <img src="https://img.shields.io/github/actions/workflow/status/wielorzeczownik/ha-toya-decoder/release.yml?branch=main&nameFilter=HACS&style=flat-square&label=HACS&labelColor=2d333b&color=2ea043" alt="HACS Validation Status"/>
  <a href="https://github.com/wielorzeczownik/ha-toya-decoder/releases/latest"><img src="https://img.shields.io/github/v/release/wielorzeczownik/ha-toya-decoder?style=flat-square&labelColor=2d333b&color=2ea043" alt="Najnowsza wersja"/></a>
  <a href="https://github.com/wielorzeczownik/ha-toya-decoder/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square&labelColor=2d333b" alt="Licencja MIT"/></a>
  <br/>
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square&logo=homeassistant&logoColor=white&labelColor=2d333b" alt="HACS Default"/></a>
  <a href="https://www.home-assistant.io/"><img src="https://img.shields.io/badge/Home%20Assistant-2024.6.0-41bdf5?style=flat-square&logo=homeassistant&logoColor=white&labelColor=2d333b" alt="Home Assistant"/></a>
</p>

<p align="center">
  <img
    src="https://raw.githubusercontent.com/wielorzeczownik/ha-toya-decoder/main/assets/toya-decoder.png"
    alt="Integracja dekodera TOYA z Home Assistant"
    width="260"
  >
</p>

Steruj **dekoderem TOYA** bezpośrednio z **Home Assistant**. Integracja udostępnia dekoder telewizji kablowej TOYA jako encję `media_player`, co umożliwia pełne sterowanie pilotem, zmianę kanałów i automatyzację – wszystko z poziomu interfejsu Home Assistant lub przez automatyzacje.

<p align="center">🇬🇧 <a href="https://github.com/wielorzeczownik/ha-toya-decoder/blob/main/README.md">English</a> | 🇵🇱 Polski</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=wielorzeczownik&repository=ha-toya-decoder&category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Otwórz w HACS"/></a>
  <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=toya_decoder"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Dodaj integrację" /></a>
</p>

## Co umożliwia integracja

- **Encja media player** dla każdego dekodera TOYA – widoczna w panelu Home Assistant
- **Sterowanie zasilaniem** – włączanie i wyłączanie dekodera TOYA z Home Assistant
- **Sterowanie głośnością** – ciszej, głośniej, wyciszenie
- **Zmiana kanałów** – kanał wyżej/niżej lub przeskoczenie bezpośrednio na wybrany numer bądź nazwę kanału
- **Przeglądarka mediów** – przeglądanie pełnej listy kanałów TOYA z poziomu interfejsu HA
- **Obsługa `media_player.play_media`** – automatyczna zmiana kanału w skryptach i automatyzacjach
- **Komendy pilota** – wysyłanie dowolnego przycisku pilota (play, pause, stop, wstecz, OK, strzałki itd.)

## Instalacja przez HACS

1. W Home Assistant otwórz **HACS → Integracje**.
2. Wyszukaj **TOYA Decoder** i zainstaluj.
3. Uruchom ponownie Home Assistant.
4. Przejdź do **Ustawienia → Urządzenia i usługi → Dodaj integrację** i wyszukaj **TOYA Decoder**.
5. Podaj dane logowania do konta TOYA (te same, których używasz w aplikacji Toya GO).

## Obsługiwane urządzenia

Integracja obsługuje dekodery TOYA bez Android TV, które zwracają niepustą wartość `smartcard` z API. Urządzenia Android TV (ATV) zwracają pusty smartcard i nie są obsługiwane.

**Znane modele legacy (bez Android TV) – powinny być kompatybilne:**

| Model                                             | Generacja |
| ------------------------------------------------- | --------- |
| Intek HD-C20CXM, HD-C20CXM Model S, HD-C20CXM PVR | 3G HD     |
| Intek HD-C63CX, HD-C64CXM                         | 3G HD     |
| Arion ARC-5510DR, ARC-5511DR                      | 3G HD     |
| Arion ARC-1010YR, ARC-1011YR, ARC-1013YR          | HD        |
| Intek C311CX                                      | SD        |

**Nieobsługiwane (Android TV):** MAXX 4K (DTC974x, DTC974y, ARC-S110ZR), MAXX 4K IPTV (ARI-U110UR), TOYA 4K (UHD-C55CX).

> [!NOTE]
> TOYA wprowadził niedawno weryfikację dwuetapową (2FA) w portalu klienta. API aplikacji Toya GO, z którego korzysta ta integracja, nie wymaga 2FA – włączenie 2FA na koncie nie ma wpływu na działanie integracji.

## Znane ograniczenia

- API nie udostępnia bezpośredniego endpointu do ustawiania kanału. Zmiana kanału jest realizowana przez emulację naciśnięć klawiszy pilota (cyfry + nawigacja), więc wynik zależy od aktualnego stanu interfejsu na ekranie. W niektórych widokach zmiana kanału wymaga potwierdzenia przyciskiem Play.
- Aktywny tryb gotowości (active standby) jest raportowany przez API jako WŁĄCZONY, nawet gdy dekoder wygląda na wyłączony.
- Pasywny tryb gotowości jest raportowany jako WYŁĄCZONY i nie można włączyć dekodera przez API.
- Błędy w mapowaniu numerów kanałów w API:
  - TVN HD jest raportowany jako kanał 5, choć fizycznie znajduje się na kanale 4.
  - Toya HD i Toya VOD są obydwa raportowane jako kanał 6.

## Zastrzeżenie

To jest nieoficjalna integracja tworzona przez społeczność, niepowiązana z firmą TOYA. Może przestać działać w przypadku zmian w API.
