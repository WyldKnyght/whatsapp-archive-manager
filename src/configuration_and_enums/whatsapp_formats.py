# src/configuration_and_enums/whatsapp_formats.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class WhatsAppFormat(Enum):
    ANDROID_US = "android_us"
    ANDROID_EU = "android_eu"
    ANDROID_24H = "android_24h"
    IOS_STANDARD = "ios_standard"
    IOS_ALT = "ios_alt"
    EUROPEAN_DOT = "european_dot"
    EUROPEAN_DASH = "european_dash"
    ASIAN_STANDARD = "asian_standard"
    UK_FORMAT = "uk_format"
    BRAZILIAN = "brazilian"
    INDIAN = "indian"
    GENERIC_24H = "generic_24h"
    US_BRACKET_AMPMPM = "us_bracket_ampm"
    UNKNOWN = "unknown"

@dataclass
class FormatInfo:
    regex: str
    date_format: str
    time_format: str
    separator: str
    timestamp_wrapper: Optional[str]
    description: str
    regions: List[str]
