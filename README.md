# 🤖 Telegram Document Converter Bot

A powerful, modular Telegram bot for converting documents and images with advanced features like custom naming, image enhancement, and multiple conversion methods.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-v20+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 📸 Image Processing
- **Multi-image to PDF conversion** (up to 50 images)
- **Image enhancement** (brightness, contrast, sharpness, auto-enhance)
- **Batch processing** with quality options
- **Smart image scaling** that fits perfectly in PDF pages

### 📄 Document Conversion
- **PDF ↔ Images** (PNG, JPEG with quality options)
- **Word → PDF** (DOCX, DOC with multiple conversion methods)
- **Excel → PDF** (XLSX, XLS with enhanced table formatting)
- **Text → PDF** (TXT, HTML, MD with proper formatting)

### ⚡ Advanced Features
- **Custom filename support** for all conversions
- **Multiple conversion methods** for reliability (LibreOffice, Pandoc, native Python)
- **Quality settings** (Low/Medium/High/Ultra DPI)
- **Auto-enhancement mode** for images
- **Smart error handling** and recovery
- **Detailed conversion statistics**
- **User settings persistence**
- **Rate limiting** and security features

### 🔒 Security & Performance
- **Safe filename sanitization**
- **File type validation** (optional)
- **Automatic temporary file cleanup**
- **Concurrent conversion processing**
- **Memory-efficient image processing**
- **Comprehensive error logging**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/telegram-document-bot.git
   cd telegram-document-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your bot token:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Installation Requirements

### Required Dependencies
```bash
pip install python-telegram-bot PyMuPDF python-docx openpyxl reportlab Pillow
```

### Optional Dependencies (for enhanced features)
```bash
pip install python-magic python-dotenv qrcode html2text markdown
```

### System Dependencies (for best conversion quality)
- **LibreOffice** (recommended for Word/Excel conversion)
  ```bash
  # Ubuntu/Debian
  sudo apt install libreoffice
  
  # macOS
  brew install --cask libreoffice
  
  # Windows: Download from https://www.libreoffice.org/
  ```

- **Pandoc** (alternative document converter)
  ```bash
  # Ubuntu/Debian
  sudo apt install pandoc
  
  # macOS
  brew install pandoc
  
  # Windows: Download from https://pandoc.org/installing.html
  ```

## ⚙️ Configuration

The bot supports extensive configuration through environment variables:

### Core Settings
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username
ADMIN_USER_ID=your_admin_user_id
```

### File Processing
```bash
MAX_FILE_SIZE=52428800          # 50MB in bytes
MAX_IMAGES_PER_PDF=50
MAX_CONCURRENT_CONVERSIONS=5
DEFAULT_IMAGE_QUALITY=medium    # low, medium, high, ultra
DEFAULT_OUTPUT_FORMAT=PNG
```

### Feature Flags
```bash
ENABLE_IMAGE_TO_PDF=true
ENABLE_PDF_TO_IMAGES=true
ENABLE_WORD_TO_PDF=true
ENABLE_EXCEL_TO_PDF=true
ENABLE_IMAGE_ENHANCEMENT=true
ENABLE_USER_SETTINGS=true
```

### Security
```bash
ENABLE_FILE_VALIDATION=false
ENABLE_FILENAME_SANITIZATION=true
MAX_FILENAME_LENGTH=255
```

### Logging
```bash
LOG_LEVEL=INFO
LOG_FILE=bot.log
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
```

See `.env.example` for all available options.

## 🎯 Usage Examples

### Basic Commands
- `/start` - Welcome message and main menu
- `/help` - Detailed help guide
- `/stats` - Your usage statistics
- `/settings` - User preferences
- `/clear` - Clear current session
- `/formats` - Supported file formats

### Image to PDF Conversion
1. Send one or multiple images to the bot
2. Choose "📄 Convert to PDF" or "📝 Custom Name"
3. Select quality settings if needed
4. Receive your PDF file

### PDF to Images Conversion
1. Send a PDF file to the bot
2. Choose "🖼️ Convert to Images"
3. Select output format (PNG/JPEG) and quality
4. Receive images as a ZIP file

### Document Conversion
1. Send Word (.docx) or Excel (.xlsx) files
2. Choose "📄 Convert to PDF"
3. Receive converted PDF with preserved formatting

### Custom Naming
1. Click "📝 Custom Name" before any conversion
2. Enter your desired filename (without extension)
3. The bot will use your custom name for the output file

### Image Enhancement
1. Send images to the bot
2. Choose "🎨 Enhance Images"
3. Select enhancement type (brightness, contrast, sharpness, auto-enhance)
4. Convert enhanced images to PDF

## 🏗️ Project Structure

```
telegram-document-bot/
├── main.py                      # Main entry point
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── config/
│   └── config.py               # Configuration management
├── utils/
│   ├── logging_setup.py        # Logging setup
│   └── security.py             # Security utilities
├── converters/
│   └── document_converter.py   # Conversion logic
└── bot/
    ├── handlers.py              # Command handlers
    ├── file_handlers.py         # File processing
    ├── callback_handlers.py     # Button interactions
    └── conversation_handlers.py # Custom naming flow
```

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
```bash
black .
flake8 .
```

### Docker Support
```bash
docker build -t telegram-document-bot .
docker run -d --env-file .env telegram-document-bot
```

## 📊 Features Matrix

| Feature | Status | Description |
|---------|--------|-------------|
| ✅ Images → PDF | Complete | Convert multiple images to PDF with scaling |
| ✅ PDF → Images | Complete | Extract PDF pages as images |
| ✅ Word → PDF | Complete | Convert DOCX/DOC to PDF |
| ✅ Excel → PDF | Complete | Convert XLSX/XLS with table formatting |
| ✅ Text → PDF | Complete | Convert TXT/HTML/MD to PDF |
| ✅ Image Enhancement | Complete | Brightness, contrast, sharpness, auto-enhance |
| ✅ Custom Naming | Complete | User-defined output filenames |
| ✅ Quality Settings | Complete | Multiple DPI options |
| ✅ User Settings | Complete | Persistent user preferences |
| ✅ Statistics | Complete | Conversion tracking |
| 🔄 Batch Processing | Partial | Multiple file processing |
| 🔄 Cloud Storage | Planned | Integration with cloud services |
| 🔄 API Endpoints | Planned | REST API for external access |

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't start:**
- Check your `TELEGRAM_BOT_TOKEN` in `.env`
- Ensure all required dependencies are installed
- Check the log files for error messages

**Conversion failures:**
- Install LibreOffice for better Word/Excel conversion
- Check file size limits (default 50MB)
- Ensure sufficient disk space for temporary files

**Image quality issues:**
- Adjust the `DEFAULT_IMAGE_QUALITY` setting
- Use manual quality selection in bot settings
- Try image enhancement features

**Permission errors:**
- Ensure the bot has write permissions in the working directory
- Check temporary file directory permissions

### Debug Mode
Enable debug logging:
```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF processing
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [Pillow](https://github.com/python-pillow/Pillow) - Image processing
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel file processing

## 🔗 Links

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Create a Bot with @BotFather](https://t.me/botfather)
- [Python Telegram Bot Library](https://python-telegram-bot.readthedocs.io/)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#🐛-troubleshooting) section
2. Search existing [Issues](https://github.com/yourusername/telegram-document-bot/issues)
3. Create a new issue with detailed information
4. Join our [Telegram Support Group](https://t.me/your_support_group)

---

⭐ **Star this repository if you find it useful!**

Made with ❤️ for the Telegram community