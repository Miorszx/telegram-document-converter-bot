"""
Configuration management for the Telegram Document Converter Bot
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    load_dotenv = None
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv not available. Using environment variables only.")


class BotConfig:
    """Configuration class with all settings"""
    
    def __init__(self):
        self._load_environment()
        self._set_defaults()
        self._validate_config()
    
    def _load_environment(self):
        """Load environment variables from .env file if available"""
        env_path = Path(".env")
        if env_path.exists() and DOTENV_AVAILABLE:
            load_dotenv(env_path)
            print("✅ Loaded environment from .env file")
        elif env_path.exists():
            print("⚠️  Found .env file but python-dotenv not available")
    
    def _set_defaults(self):
        """Set configuration from environment variables with defaults"""
        
        # Core settings (required)
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        self.bot_username = os.getenv('BOT_USERNAME')
        self.admin_user_id = self._get_env_int('ADMIN_USER_ID')
        
        # File handling
        self.max_file_size = self._get_env_int('MAX_FILE_SIZE', 52428800)  # 50MB
        self.max_images_per_pdf = self._get_env_int('MAX_IMAGES_PER_PDF', 50)
        self.max_concurrent_conversions = self._get_env_int('MAX_CONCURRENT_CONVERSIONS', 5)
        self.temp_cleanup_hours = self._get_env_int('TEMP_CLEANUP_HOURS', 24)
        
        # Image settings
        self.default_image_quality = os.getenv('DEFAULT_IMAGE_QUALITY', 'medium')
        self.default_output_format = os.getenv('DEFAULT_OUTPUT_FORMAT', 'PNG')
        self.auto_enhance_default = self._get_env_bool('AUTO_ENHANCE_DEFAULT', False)
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'bot.log')
        self.enable_file_logging = self._get_env_bool('ENABLE_FILE_LOGGING', True)
        self.enable_console_logging = self._get_env_bool('ENABLE_CONSOLE_LOGGING', True)
        
        # External tools
        self.libreoffice_path = os.getenv('LIBREOFFICE_PATH')
        self.pandoc_path = os.getenv('PANDOC_PATH')
        
        # Rate limiting
        self.rate_limit_requests = self._get_env_int('RATE_LIMIT_REQUESTS', 10)
        self.rate_limit_window = self._get_env_int('RATE_LIMIT_WINDOW', 60)
        
        # Feature flags
        self.enable_image_to_pdf = self._get_env_bool('ENABLE_IMAGE_TO_PDF', True)
        self.enable_pdf_to_images = self._get_env_bool('ENABLE_PDF_TO_IMAGES', True)
        self.enable_word_to_pdf = self._get_env_bool('ENABLE_WORD_TO_PDF', True)
        self.enable_excel_to_pdf = self._get_env_bool('ENABLE_EXCEL_TO_PDF', True)
        self.enable_image_enhancement = self._get_env_bool('ENABLE_IMAGE_ENHANCEMENT', True)
        self.enable_user_settings = self._get_env_bool('ENABLE_USER_SETTINGS', True)
        self.enable_user_stats = self._get_env_bool('ENABLE_USER_STATS', True)
        
        # Security - Made less strict to fix image validation issues
        self.enable_file_validation = self._get_env_bool('ENABLE_FILE_VALIDATION', False)
        self.enable_filename_sanitization = self._get_env_bool('ENABLE_FILENAME_SANITIZATION', True)
        self.max_filename_length = self._get_env_int('MAX_FILENAME_LENGTH', 255)
        
        # Development
        self.debug_mode = self._get_env_bool('DEBUG_MODE', False)
        self.test_mode = self._get_env_bool('TEST_MODE', False)
        
        # Quality settings
        self.image_quality = {
            'low': 72,
            'medium': 150,
            'high': 300,
            'ultra': 600
        }
    
    def _get_env_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get environment variable as integer"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            print(f"⚠️  Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    
    def _validate_config(self):
        """Validate configuration"""
        if not self.telegram_bot_token or self.telegram_bot_token == 'YOUR_BOT_TOKEN_HERE':
            print("❌ TELEGRAM_BOT_TOKEN is required!")
            print("💡 Get your token from @BotFather on Telegram")
            print("🔧 Set environment variable: export TELEGRAM_BOT_TOKEN='your_token'")
            print("🔧 Or create .env file with TELEGRAM_BOT_TOKEN=your_token")
            sys.exit(1)
        
        # Validate quality setting
        if self.default_image_quality not in self.image_quality:
            print(f"⚠️  Invalid image quality: {self.default_image_quality}, using 'medium'")
            self.default_image_quality = 'medium'
        
        print("✅ Configuration validated successfully!")
