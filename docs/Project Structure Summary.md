# Project Structure Summary

whatsapp_chat_export/
│
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── date_utils.py          # Date parsing and validation
│   │   ├── path_utils.py          # Path handling
│   │   ├── color_utils.py         # Color mapping
│   │   └── string_utils.py        # String cleaning and formatting
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── message.py             # Message data class
│   │   ├── chat.py                # Chat data class
│   │   └── date_range.py          # DateRange data class
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── date_format_detector.py    # Date format detection
│   │   ├── sender_extractor.py        # Sender extraction
│   │   └── message_parser.py          # Main message parser
│   │
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── css_generator.py       # CSS generation
│   │   ├── html_builder.py        # HTML structure building
│   │   └── html_renderer.py       # Main HTML renderer
│   │
│   ├── io/
│   │   ├── __init__.py
│   │   ├── file_writer.py         # File writing operations
│   │   ├── zip_handler.py         # ZIP file handling
│   │   └── file_picker.py         # File picker UI
│   │
│   └── chat_export.py             # Main orchestrator
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
└── main.py                    # Entry point
