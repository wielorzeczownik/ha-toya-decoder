"""Constants and enums for the Toya decoder integration."""

from __future__ import annotations

from enum import IntEnum, StrEnum

DOMAIN = "toya_decoder"


class RemoteCommand(StrEnum):
    """Supported remote control commands."""

    PLAYPAUSE = "playpause"
    PREV = "prev"
    LAST = "last"
    AUDIO = "audio"
    PVR = "pvr"
    STOP = "stop"
    REC = "rec"
    BLUE = "blue"
    YELLOW = "yellow"
    GREEN = "green"
    RED = "red"
    MENU = "menu"
    MUTE = "mute"
    LIST = "list"
    DIGIT_0 = "0"
    DIGIT_1 = "1"
    DIGIT_2 = "2"
    DIGIT_3 = "3"
    DIGIT_4 = "4"
    DIGIT_5 = "5"
    DIGIT_6 = "6"
    DIGIT_7 = "7"
    DIGIT_8 = "8"
    DIGIT_9 = "9"
    POWER = "power"
    VOD = "vod"
    EPG = "epg"
    OPT = "opt"
    BACK = "back"
    OK = "ok"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FFW = "ffw"


REMOTE_COMMANDS = [cmd.value for cmd in RemoteCommand]


class DeviceStatus(IntEnum):
    """Decoder power state values reported by the API."""

    OFF = 0
    ON = 1
    ATV = 2
    UNKNOWN = -1
