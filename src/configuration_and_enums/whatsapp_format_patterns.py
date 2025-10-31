# src/configuration_and_enums/whatsapp_format_patterns.py

from typing import Dict
from .whatsapp_formats import WhatsAppFormat, FormatInfo

# Dictionary of supported WhatsApp format patterns.
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
    WhatsAppFormat.IOS_US_BRACKET_12H: FormatInfo(
        regex=r'^\[(\d{4}-\d{2}-\d{2}),[\s\u202f]+(\d{1,2}:\d{2}:\d{2})[\s\u202f]*([AP]M)\][\s\u202f]+([^:]+):[\s\u202f]*(.+)$',
        date_format='%Y-%m-%d',
        time_format='%I:%M:%S %p',
        separator='] ',
        timestamp_wrapper='[]',
        description='iOS/WhatsApp US format with brackets and Unicode spaces (YYYY-MM-DD, H:MM:SS AM/PM)',
        regions=['US', 'Canada', 'iOS exports']
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
        regex=r'^\[(\d{4}-\d{2}-\d{2}),\s(\d{1,2}:\d{2}:\d{2})\s?([AP]M)\]\s([^:]+):\s(.+)$',
        date_format='%Y-%m-%d',
        time_format='%I:%M:%S%p',
        separator='] ',
        timestamp_wrapper='[]',
        description='US/International bracket format with AM/PM (YYYY-MM-DD, h:mm:ssAM/PM)',
        regions=['Modern WhatsApp Export', 'US', 'International']
    ),
    WhatsAppFormat.CUSTOM_COMMA_TIME: FormatInfo(
        regex=r'^\d{4}-\d{2}-\d{2}, \d{6} [AP]M(?: [^ ]+)? .+',
        date_format='%Y-%m-%d',
        time_format='%I%M%S %p',
        separator=' ',
        timestamp_wrapper=None,
        description='YYYY-MM-DD, HHMMSS AM/PM Name Message (no brackets, comma after date, no colon)',
        regions=['Export variant', 'Custom detected']
    ),
    WhatsAppFormat.CUSTOM_COMMA_TIME: FormatInfo(
        # Change regex to make sender optional (username may be missing)
        regex=r'^\d{4}-\d{2}-\d{2}, \d{6} [AP]M(?: [^ ]+)? .+',
        date_format="Y-m-d",
        time_format="IMS p",
        separator=" ",
        timestamp_wrapper=None,
        description="YYYY-MM-DD, HHMMSS AMPM Name Message (sender optional)",
        regions=["Export variant", "Custom detected"]
    ),
    WhatsAppFormat.US_COMMA_COMPACT: FormatInfo(
        regex=r'^\d{4}-\d{2}-\d{2}, \d{6} [AP]M(?: [^ ]+)? .+',
        date_format="Y-m-d",
        time_format="IMS p",
        separator=" ",
        timestamp_wrapper=None,
        description="US/Canada WhatsApp export (sender optional)",
        regions=["US", "Canada", "WhatsApp direct"]
    ),
    WhatsAppFormat.US_COMPACT_NOSEP: FormatInfo(
        regex=r'^\d{4}-\d{2}-\d{2}, \d{6} [AP]M(?: [^ ]+)? .+',
        date_format="Y-m-d",
        time_format="IMS p",
        separator=" ",
        timestamp_wrapper=None,
        description="US/Canada export no separator, sender optional",
        regions=["US", "Canada", "WhatsApp direct"]
    ),
    WhatsAppFormat.BRACKETED_US: FormatInfo(
        regex=r'^\[(?P<date>\d{4}-\d{2}-\d{2}), (?P<time>\d{1,2}:\d{2}:\d{2}\s*[AP]M)\] (?P<sender>[^:]+): (?P<message>.+)$',
        date_format='%Y-%m-%d',
        time_format='%I:%M:%S %p',
        separator='] ',
        timestamp_wrapper='[]',
        description='Bracketed WhatsApp export [YYYY-MM-DD, H:MM:SS AM/PM] Sender: Message',
        regions=['US', 'iOS', 'Modern WhatsApp Export']
    ),
}
