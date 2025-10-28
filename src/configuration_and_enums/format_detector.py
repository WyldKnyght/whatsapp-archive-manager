# configuration_and_enums/format_detector.py

import re
from typing import Dict, Tuple, Optional, List
from enum import Enum
from dataclasses import dataclass
import chardet

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

class FormatDetector:
    FORMATS: Dict[WhatsAppFormat, FormatInfo] = {
        WhatsAppFormat.ANDROID_US: FormatInfo(
            regex=r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*([^:]+):\s*(.+)$',
            date_format='%m/%d/%y',
            time_format='%I:%M %p',
            separator=' - ',
            timestamp_wrapper=None,
            description='Android US format',
            regions=['US', 'Philippines', 'Canada']
        ),
        WhatsAppFormat.ANDROID_EU: FormatInfo(
            regex=r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d/%m/%Y',
            time_format='%H:%M',
            separator=' - ',
            timestamp_wrapper=None,
            description='Android European format',
            regions=['UK', 'Ireland', 'Australia', 'New Zealand']
        ),
        WhatsAppFormat.ANDROID_24H: FormatInfo(
            regex=r'^(\d{1,2}/\d{1,2}/\d{4}),\s+(\d{2}:\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d/%m/%Y',
            time_format='%H:%M:%S',
            separator=' - ',
            timestamp_wrapper=None,
            description='Android with seconds',
            regions=['Various']
        ),
        WhatsAppFormat.IOS_STANDARD: FormatInfo(
            regex=r'^\[(\d{1,2}/\d{1,2}/\d{4}),\s+(\d{2}:\d{2}:\d{2})\]\s+([^:]+):\s*(.+)$',
            date_format='%d/%m/%Y',
            time_format='%H:%M:%S',
            separator='] ',
            timestamp_wrapper='[]',
            description='iOS standard format',
            regions=['Global iOS']
        ),
        WhatsAppFormat.IOS_ALT: FormatInfo(
            regex=r'^\[(\d{1,2}/\d{1,2}/\d{4}),\s+(\d{1,2}:\d{2}:\d{2}\s*[AP]M)\]\s+([^:]+):\s*(.+)$',
            date_format='%d/%m/%Y',
            time_format='%I:%M:%S %p',
            separator='] ',
            timestamp_wrapper='[]',
            description='iOS 12-hour',
            regions=['US iOS']
        ),
        WhatsAppFormat.EUROPEAN_DOT: FormatInfo(
            regex=r'^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s+(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d.%m.%y',
            time_format='%H:%M',
            separator=' - ',
            timestamp_wrapper=None,
            description='European dot format',
            regions=['Germany', 'Austria', 'Switzerland', 'Poland']
        ),
        WhatsAppFormat.EUROPEAN_DASH: FormatInfo(
            regex=r'^(\d{4}-\d{2}-\d{2}),?\s+(\d{2}:\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%Y-%m-%d',
            time_format='%H:%M:%S',
            separator=' - ',
            timestamp_wrapper=None,
            description='ISO-like format',
            regions=['Europe']
        ),
        WhatsAppFormat.ASIAN_STANDARD: FormatInfo(
            regex=r'^(\d{4}/\d{1,2}/\d{1,2}),?\s+(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%Y/%m/%d',
            time_format='%H:%M',
            separator=' - ',
            timestamp_wrapper=None,
            description='Asian year-first',
            regions=['China', 'Japan', 'Korea']
        ),
        WhatsAppFormat.UK_FORMAT: FormatInfo(
            regex=r'^(\d{2}/\d{2}/\d{4}),\s+(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d/%m/%Y',
            time_format='%H:%M',
            separator=' - ',
            timestamp_wrapper=None,
            description='UK format',
            regions=['UK', 'Ireland']
        ),
        WhatsAppFormat.BRAZILIAN: FormatInfo(
            regex=r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d/%m/%Y',
            time_format='%H:%M',
            separator=' - ',
            timestamp_wrapper=None,
            description='Brazilian format',
            regions=['Brazil', 'Portugal']
        ),
        WhatsAppFormat.INDIAN: FormatInfo(
            regex=r'^(\d{1,2}/\d{1,2}/\d{2}),\s+(\d{1,2}:\d{2}\s*[ap]m)\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d/%m/%y',
            time_format='%I:%M %p',
            separator=' - ',
            timestamp_wrapper=None,
            description='Indian format',
            regions=['India']
        ),
        WhatsAppFormat.GENERIC_24H: FormatInfo(
            regex=r'^(\d{1,2}/\d{1,2}/\d{2,4})\s+(\d{2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            date_format='%d/%m/%y',
            time_format='%H:%M',
            separator=' - ',
            timestamp_wrapper=None,
            description='Generic 24-hour',
            regions=['Various']
        ),
        WhatsAppFormat.US_BRACKET_AMPMPM: FormatInfo(
            # Handles [2022-05-05, 9:13:12 PM] Name: Message
            regex=r'^\[(\d{4}-\d{2}-\d{2}),\s(\d{1,2}:\d{2}:\d{2})[\u202f\s]?([AP]M)\]\s([^:]+):\s(.+)$',
            date_format='%Y-%m-%d',
            time_format='%I:%M:%S%p',  # No space before %p, since AM/PM may be attached directly in some cases
            separator='] ',
            timestamp_wrapper='[]',
            description='US/International bracket format with AM/PM (YYYY-MM-DD, h:mm:ssAM/PM) [with Unicode narrow space support]',
            regions=['Modern WhatsApp Export', 'US', 'International']
        ),

    }

    @staticmethod
    def detect_encoding(file_path: str, sample_size: int = 10000) -> Tuple[str, float]:
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
            if not raw_data:
                return 'utf-8', 0.0
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0.0)
            if encoding == 'ISO-8859-1' and confidence < 0.7:
                encoding = 'utf-8'
            elif encoding in ['ascii', 'ASCII']:
                encoding = 'utf-8'
            elif encoding and 'UTF-16' in encoding.upper():
                encoding = 'utf-16'
            return encoding, confidence
        except Exception:
            return 'utf-8', 0.0

    @staticmethod
    def detect_format(file_path: str, encoding: Optional[str] = None, sample_lines: int = 20, min_confidence: float = 0.3) -> Tuple[WhatsAppFormat, float, Dict[WhatsAppFormat, int]]:
        if encoding is None:
            encoding, _ = FormatDetector.detect_encoding(file_path)
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                lines = [f.readline().strip() for _ in range(sample_lines)]
        except Exception:
            return WhatsAppFormat.UNKNOWN, 0.0, {}
        lines = [line for line in lines if line and len(line) > 10]
        if not lines:
            return WhatsAppFormat.UNKNOWN, 0.0, {}
        format_scores: Dict[WhatsAppFormat, int] = {fmt: 0 for fmt in FormatDetector.FORMATS}
        for line in lines:
            for fmt, info in FormatDetector.FORMATS.items():
                if re.match(info.regex, line, re.IGNORECASE):
                    format_scores[fmt] += 1
        if not any(format_scores.values()):
            return WhatsAppFormat.UNKNOWN, 0.0, format_scores
        best_format, match_count = max(format_scores.items(), key=lambda x: x[1])
        total_lines = len(lines)
        confidence = match_count / total_lines if total_lines > 0 else 0.0
        if confidence < min_confidence:
            return WhatsAppFormat.UNKNOWN, confidence, format_scores
        return best_format, confidence, format_scores

    @staticmethod
    def get_format_info(format_type: WhatsAppFormat) -> Optional[FormatInfo]:
        return FormatDetector.FORMATS.get(format_type)

    @staticmethod
    def list_supported_formats() -> Dict[str, str]:
        return {fmt.value: info.description for fmt, info in FormatDetector.FORMATS.items()}

    @staticmethod
    def validate_format(file_path: str, expected_format: WhatsAppFormat, encoding: Optional[str] = None) -> bool:
        detected_format, confidence, _ = FormatDetector.detect_format(file_path, encoding)
        return detected_format == expected_format and confidence > 0.5
