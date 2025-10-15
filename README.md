# WhatsApp Archive Manager

A clean, modular Python tool to **manage and export WhatsApp chat archives** to beautiful HTML files—leveraging separation of concerns, best practices, and a simple interactive experience.

***

## 📋 Table of Contents

- [WhatsApp Archive Manager](#whatsapp-archive-manager)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗️ Architecture](#️-architecture)
    - [Overview](#overview)
  - [🚀 Installation](#-installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [💻 Usage](#-usage)
    - [Interactive Mode (the ONLY Mode)](#interactive-mode-the-only-mode)
  - [📁 Project Structure](#-project-structure)
  - [🎯 Design Principles](#-design-principles)
  - [🔧 Development](#-development)
    - [Running Tests](#running-tests)
  - [📊 Metrics](#-metrics)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📞 Support](#-support)

***

## ✨ Features

- **Export WhatsApp chats** to HTML with media support
- **Date range filtering:** Select and limit by date interactively
- **Easy, interactive mode only:** GUI file selection and guided prompts
- **No command-line arguments or automation complexity**
- **Cross-platform:** Windows file dialog or Tkinter-powered picker
- **Modern Python project structure and modular codebase**

***

## 🏗️ Architecture

This version follows **Single Responsibility Principle (SRP)**, **Separation of Concerns (SoC)**, and **DRY**—all in a clean `/src` hierarchy.

### Overview

┌─────────────┐
│  main.py    │  ← Interactive entry point (no CLI args)
└────┬────────┘
     │
     ▼
┌────────────────────────┐
│ ChatExportOrchestrator │  ← Coordinates workflow
└───────────┬────────────┘
            │
 ┌──────────┴──────┬──────────┬───────────┐
 ▼                ▼           ▼           ▼
Parsers      Renderers       I/O         Utils
   │             │            │            │
   ▼             ▼            ▼            ▼
┌────────────────────────────────────────────┐
│                Models                      │
└────────────────────────────────────────────┘

***

## 🚀 Installation

### Prerequisites

- Python **3.8** or higher
- `pip` package manager

### Steps

1. **Clone or download** the project:
    git clone <https://github.com/WyldKnyght/whatsapp-archive-manager.git>
    cd whatsapp-archive-manager

2. **Create a virtual environment** (recommended):
    python -m venv venv

    venv\Scripts\activate

3. **Install dependencies**:
    pip install -r requirements.txt

***

## 💻 Usage

### Interactive Mode (the ONLY Mode)

Run this from the root project folder:

python main.py

You will be guided through:

1. **Selecting a WhatsApp ZIP archive** (Windows file dialog or Tkinter GUI)
2. **Choosing your name** from chat participants (console prompt)
3. **Entering a date range** (optional, via prompts)
4. **Opening the results in your browser** (prompted)

***

## 📁 Project Structure

whatsapp-archive-manager/
│
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── docs/
│   ├── Documentation.md
│   └── migration-guide.md
├── tests/
├── src/
│   ├── chat_export.py
│   ├── io/
│   │   ├── file_picker.py
│   │   ├── file_writer.py
│   │   └── zip_handler.py
│   ├── models/
│   │   ├── chat.py
│   │   ├── date_range.py
│   │   └── message.py
│   ├── parsers/
│   │   ├── date_format_detector.py
│   │   ├── message_parser.py
│   │   └── sender_extractor.py
│   ├── renderers/
│   │   ├── css_generator.py
│   │   ├── html_builder.py
│   │   └── html_renderer.py
│   ├── utils/
│   │   ├── color_utils.py
│   │   ├── date_utils.py
│   │   ├── path_utils.py
│   │   └── string_utils.py
│   └── validators.py         # User interaction/validation helpers
└── ...

- **All core code** is within `/src`
- **No legacy CLI or positional argument support**

***

## 🎯 Design Principles

- **Single Responsibility Principle:** Each class/module does one thing
- **Separation of Concerns:** Parsing, rendering, IO, utilities
- **DRY:** No unnecessary repetition
- **Low Coupling:** All parts have clear interfaces
- **High Cohesion:** Related logic stays together

***

## 🔧 Development

### Running Tests

```bash
python -m pytest tests/
mypy src/
flake8 src/
black src/
```

***

## 📊 Metrics

| Version             | Structure            | Coupling      | Testability    | Maintainability  |
|---------------------|---------------------|---------------|---------------|------------------|
| Monolithic (legacy) | Single large file   | High          | Low           | Hard             |
| Refactored (this)   | Many small modules  | Low           | High          | Easy             |

***

## 🤝 Contributing

- Stick to the `src`-based modular layout
- One class/module, one responsibility
- Update docs for new features

***

## 📄 License

MIT License — see `LICENSE`

***

## 🙏 Acknowledgments

Original monolithic code refactored for SOLID principles and modern Python standards.

***

## 📞 Support

- Open issues on GitHub
- See `/docs` for migration notes and best practices

***

**Version:** 1.0.0  
**Last Updated:** October 2025

***
