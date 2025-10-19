class DateFormats:
    """Configuration for supported date formats"""
    FORMATS = [
        '%d/%m/%Y, %H:%M:%S',      # Common format
        '%m/%d/%Y, %H:%M:%S',      # Common format
        '%Y/%m/%d, %H:%M:%S',      # Common format
        '%d/%m/%Y, %H:%M',         # Common format (no seconds)
        '%m/%d/%Y, %H:%M',         # Common format (no seconds)
        '%Y/%m/%d, %H:%M',         # Common format (no seconds)
        '%d/%m/%y, %H:%M',         # Android format
        '%m/%d/%y, %H:%M',         # Android format
        '%Y-%m-%d, %H:%M:%S',      # ISO-like format
        '%Y-%m-%dT%H:%M:%S',       # ISO 8601
        '%Y-%m-%dT%H:%M:%S.%f',    # ISO 8601 with microseconds
        '%d-%b-%Y, %H:%M:%S',      # Day-Month-Year
        '%d-%b-%y, %H:%M:%S',      # Day-Month-Year (short)
        '%d %b %Y, %H:%M:%S',      # Day Month Year
        '%d %b %y, %H:%M:%S'       # Day Month Year (short)
    ]
