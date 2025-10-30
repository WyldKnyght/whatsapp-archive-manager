# src/configuration_and_enums/format_detector.py

import re
from typing import Dict, Tuple, Optional
import chardet
from .whatsapp_formats import WhatsAppFormat, FormatInfo
from .whatsapp_format_patterns import FORMATS

class FormatDetectionStrategyInterface:
    """Interface for format detection strategies."""
    def detect_format(self, sample_lines: list) -> Tuple[WhatsAppFormat, float, Dict[WhatsAppFormat, int]]:
        raise NotImplementedError

class DefaultFormatDetectionStrategy(FormatDetectionStrategyInterface):
    """Default regex-based detection across formats."""
    def __init__(self, formats: Dict[WhatsAppFormat, FormatInfo]):
        self.formats = formats

    def detect_format(self, sample_lines: list, min_confidence: float = 0.3) -> Tuple[WhatsAppFormat, float, Dict[WhatsAppFormat, int]]:
        lines = [line for line in sample_lines if line and len(line) > 10]
        if not lines:
            return WhatsAppFormat.UNKNOWN, 0.0, {}
        format_scores: Dict[WhatsAppFormat, int] = {fmt: 0 for fmt in self.formats}
        for line in lines:
            for fmt, info in self.formats.items():
                if re.match(info.regex, line, re.IGNORECASE):
                    format_scores[fmt] += 1
        if not any(format_scores.values()):
            return WhatsAppFormat.UNKNOWN, 0.0, format_scores
        best_format, match_count = max(format_scores.items(), key=lambda x: x[1])
        confidence = match_count / len(lines)
        if confidence < min_confidence:
            return WhatsAppFormat.UNKNOWN, confidence, format_scores
        return best_format, confidence, format_scores

class FormatDetector:
    FORMATS = FORMATS

    def __init__(self, detection_strategy: FormatDetectionStrategyInterface = None):
        self.detection_strategy = detection_strategy or DefaultFormatDetectionStrategy(self.FORMATS)

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

    def detect_format(
        self,
        file_path: str,
        encoding: Optional[str] = None,
        sample_lines: int = 20,
        min_confidence: float = 0.3
    ) -> Tuple[WhatsAppFormat, float, Dict[WhatsAppFormat, int]]:
        if encoding is None:
            encoding, _ = FormatDetector.detect_encoding(file_path)
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                lines = [f.readline().strip().replace('\u202f', ' ').replace('\xa0', ' ') for _ in range(sample_lines)]
        except Exception:
            return WhatsAppFormat.UNKNOWN, 0.0, {}
        return self.detection_strategy.detect_format(lines, min_confidence)

    @staticmethod
    def get_format_info(format_type: WhatsAppFormat) -> Optional[FormatInfo]:
        return FormatDetector.FORMATS.get(format_type)

    @staticmethod
    def list_supported_formats() -> Dict[str, str]:
        return {fmt.value: info.description for fmt, info in FormatDetector.FORMATS.items()}

    def validate_format(self, file_path: str, expected_format: WhatsAppFormat, encoding: Optional[str] = None) -> bool:
        detected_format, confidence, _ = self.detect_format(file_path, encoding)
        return detected_format == expected_format and confidence > 0.5
