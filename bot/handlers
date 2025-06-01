"""
Bot handlers for the Telegram Document Converter Bot
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from config.config import BotConfig
from utils.security import SecurityManager


class BotHandlers:
    """Contains all bot command and callback handlers"""
    
    def __init__(self, config: BotConfig, user_data: dict, security: SecurityManager):
        self.config = config
        self.user_data = user_data
        self.security = security
        self.logger = logging.getLogger(__name__)
    
    def _initialize_user_data(self, user_id: int):
        """Initialize user data if not exists"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'images': [],
                'conversions': 0,
                'files_processed': 0,
                'join_date': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'settings': {
                    'quality': self.config.default_image_quality,
                    'format': self.config.default_output_format,
                    'auto_enhance': self.config.auto_enhance_default
                },
                'pending_conversion': None,  # For custom naming
                'custom_filename': None
            }

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with proper back button behavior"""
        user = update.effective_user
        user_id = user.id
        
        # Initialize user data
        self._initialize_user_data(user_id)
        
        welcome_text = f"""
🚀 *Welcome {escape_markdown(user.first_name, version=2)}\\!* 🚀

I'm your *Advanced Document Converter Bot* with supercharged features\\!

🎯 *What I Can Do:*

📸 *Image Processing*
• Convert images to PDF \\(up to {self.config.max_images_per_pdf} images\\)
• Enhance images \\(brightness, contrast, sharpness\\)
• Batch processing with quality options
• Auto\\-enhancement mode

📄 *Document Conversion*
• PDF ↔ Images \\(multiple formats\\)
• Word → PDF \\(DOCX, DOC\\)
• Excel → PDF \\(XLSX, XLS\\) with proper formatting
• Text files → PDF \\(TXT, HTML, MD\\)

⚡ *Advanced Features*
• Multiple conversion methods for reliability
• Quality settings \\(Low/Medium/High/Ultra\\)
• Custom filename support
• Smart error handling and recovery
• Detailed conversion statistics

📊 File size limit: {self.config.max_file_size // (1024*1024)}MB
🔒 All files are processed securely and deleted after conversion

*Quick Start:* Just send me any file and I'll show you the magic\\! ✨
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 Help Guide", callback_data="show_help"),
             InlineKeyboardButton("🎛️ Settings", callback_data="show_settings")],
            [InlineKeyboardButton("📊 My Stats", callback_data="show_stats"),
             InlineKeyboardButton("📋 Supported Formats", callback_data="show_formats")],
            [InlineKeyboardButton("🧹 Clear Session", callback_data="clear_session")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 *Detailed Help Guide* 📚

🔹 *Image to PDF Conversion:*
   • Send me one or multiple photos
   • I'll ask if you want to combine them
   • Choose enhancement options
   • Get your PDF instantly!

🔹 *PDF to Images:*
   • Send me a PDF file
   • I'll convert each page to an image
   • Choose output quality
   • Receive images as a ZIP file

🔹 *Word to PDF:*
   • Send me a .docx file
   • Get a PDF version back
   • Formatting preserved!

🔹 *Excel to PDF:*
   • Send me a .xlsx file
   • Get a properly formatted PDF
   • Tables with colors and borders!

🔹 *Custom Naming:*
   • Click "📝 Custom Name" before converting
   • Choose your own filename
   • File extension added automatically

🔹 *Commands:*
   • /start - Welcome message
   • /help - This help guide
   • /stats - Your usage statistics
   • /clear - Clear current session
   • /settings - User preferences
   • /formats - Supported formats
   • /cancel - Cancel custom naming

🔹 *Tips:*
   • 💡 Send multiple images for batch PDF creation
   • 🎨 Use enhancement options for better quality
   • 📦 Large files are automatically compressed
   • ⚡ Processing is usually very fast!

*Supported Formats:*
📸 Images: JPG, PNG, GIF, BMP, TIFF
📄 Documents: PDF, DOCX, XLSX, TXT
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        stats = self.user_data[user_id]
        
        conversions = stats.get('conversions', 0)
        files_processed = stats.get('files_processed', 0)
        join_date = stats.get('join_date', 'Unknown')
        last_used = stats.get('last_used', 'Never')
        
        # Parse dates for better display
        try:
            if join_date != 'Unknown':
                join_dt = datetime.fromisoformat(join_date)
                join_display = join_dt.strftime('%Y-%m-%d')
            else:
                join_display = 'Unknown'
                
            if last_used != 'Never':
                last_dt = datetime.fromisoformat(last_used)
                last_display = last_dt.strftime('%Y-%m-%d %H:%M')
            else:
                last_display = 'Never'
        except:
            join_display = 'Unknown'
            last_display = 'Never'
        
        stats_text = f"""
📊 *Your Statistics* 📊

🔄 Total Conversions: {conversions}
📁 Files Processed: {files_processed}
📅 Member Since: {join_display}
🕐 Last Used: {last_display}

🏆 Keep converting to unlock achievements!
        """
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def clear_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear user session data"""
        user_id = update.effective_user.id
        if user_id in self.user_data:
            # Keep stats but clear temporary data
            current_data = self.user_data[user_id]
            self.user_data[user_id] = {
                'images': [],
                'conversions': current_data.get('conversions', 0),
                'files_processed': current_data.get('files_processed', 0),
                'join_date': current_data.get('join_date', datetime.now().isoformat()),
                'last_used': current_data.get('last_used', datetime.now().isoformat()),
                'settings': current_data.get('settings', {
                    'quality': self.config.default_image_quality,
                    'format': self.config.default_output_format,
                    'auto_enhance': self.config.auto_enhance_default
                }),
                'pending_conversion': None,
                'custom_filename': None
            }
        
        await update.message.reply_text("🧹 Session cleared! Ready for new conversions! ✨")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """User settings management"""
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        settings = self.user_data[user_id]['settings']
        
        settings_text = f"""
🎛️ *Your Current Settings*

📸 *Image Quality:* {settings.get('quality', 'medium').title()}
🖼️ *Output Format:* {settings.get('format', 'PNG')}
✨ *Auto-Enhance:* {'Enabled' if settings.get('auto_enhance', False) else 'Disabled'}

*Quality Options:*
• Low (72 DPI) - Faster, smaller files
• Medium (150 DPI) - Balanced quality and size
• High (300 DPI) - High quality, larger files
• Ultra (600 DPI) - Maximum quality
        """
        
        keyboard = [
            [InlineKeyboardButton("📸 Change Quality", callback_data="setting_quality"),
             InlineKeyboardButton("🖼️ Change Format", callback_data="setting_format")],
            [InlineKeyboardButton("✨ Toggle Auto-Enhance", callback_data="setting_auto_enhance")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def formats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show supported formats"""
        formats_text = """
📋 *Supported File Formats*

📸 *Image Formats:*
• Input: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP, ICO
• Output: PNG, JPEG, PDF

📄 *Document Formats:*
• PDF (input/output)
• Word: DOCX, DOC → PDF
• Excel: XLSX, XLS → PDF (with formatting!)
• Text: TXT, HTML, HTM, MD → PDF

🔄 *Conversion Types:*
• Images → PDF (combine multiple)
• PDF → Images (extract pages)
• Documents → PDF
• Image enhancement
• Batch processing

⚡ *Processing Limits:*
• Max file size: 50MB
• Max images per PDF: 50
• Concurrent conversions: 5

🔒 *Security Features:*
• Safe filename checking
• Automatic cleanup
• No data retention

✨ *New Features:*
• Custom filename support
• Enhanced Excel formatting
• Improved navigation
        """
        
        await update.message.reply_text(formats_text, parse_mode=ParseMode.MARKDOWN)

    async def cancel_naming(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel custom naming"""
        user_id = update.effective_user.id
        if user_id in self.user_data:
            self.user_data[user_id]['pending_conversion'] = None
            self.user_data[user_id]['custom_filename'] = None
        
        await update.message.reply_text("❌ Custom naming cancelled.")
        from telegram.ext import ConversationHandler
        return ConversationHandler.END

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        self.logger.error("Exception while handling an update:", exc_info=context.error)
        
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An unexpected error occurred. Please try again later."
                )
            except Exception:
                pass
