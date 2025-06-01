"""
Logging setup utilities for the Telegram Document Converter Bot
"""

import logging
from config.config import BotConfig


def setup_logging(config: BotConfig):
    """Setup logging based on configuration"""
    handlers = []
    
    # Console handler
    if config.enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(console_handler)
    
    # File handler
    if config.enable_file_logging and config.log_file:
        try:
            file_handler = logging.FileHandler(config.log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            handlers.append(file_handler)
        except Exception as e:
            print(f"⚠️  Could not setup file logging: {e}")
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        handlers=handlers,
        force=True
    )
