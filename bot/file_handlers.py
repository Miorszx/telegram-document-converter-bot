"""
File handlers for the Telegram Document Converter Bot
"""

import os
import uuid
import logging
from datetime import datetime
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from config.config import BotConfig
from utils.security import SecurityManager


class FileHandlers:
    """Handles file processing for the bot"""
    
    def __init__(self, config: BotConfig, user_data: dict, security: SecurityManager, temp_base_dir: str):
        self.config = config
        self.user_data = user_data
        self.security = security
        self.temp_base_dir = temp_base_dir
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
                'pending_conversion': None,
                'custom_filename': None
            }

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Photo handling with proper back button behavior and file path fixes"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        try:
            # Download photo
            photo = update.message.photo[-1]  # Get highest resolution
            file = await context.bot.get_file(photo.file_id)
            
            # Check file size
            if file.file_size and file.file_size > self.config.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large! Maximum size is {self.config.max_file_size // (1024*1024)}MB."
                )
                return
            
            # Create user temp directory
            user_temp_dir = os.path.join(self.temp_base_dir, str(user_id))
            os.makedirs(user_temp_dir, exist_ok=True)
            
            # Generate safe filename
            file_ext = '.jpg'
            safe_filename = f"img_{len(self.user_data[user_id]['images'])}_{uuid.uuid4().hex[:8]}{file_ext}"
            image_path = os.path.join(user_temp_dir, safe_filename)
            
            # Download file properly
            await file.download_to_drive(image_path)
            
            # Verify file was downloaded
            if not os.path.exists(image_path):
                await update.message.reply_text("❌ Error downloading image. Please try again.")
                return
            
            # Validate file only if enabled and be more permissive
            if self.config.enable_file_validation:
                try:
                    # Try to open with PIL to validate it's an image
                    test_img = Image.open(image_path)
                    test_img.close()
                except Exception as e:
                    await update.message.reply_text("❌ Invalid image file!")
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    return
            
            # Add to user's collection
            self.user_data[user_id]['images'].append(image_path)
            self.user_data[user_id]['files_processed'] += 1
            self.user_data[user_id]['last_used'] = datetime.now().isoformat()
            
            # Check if we've reached the limit
            if len(self.user_data[user_id]['images']) >= self.config.max_images_per_pdf:
                await update.message.reply_text(
                    f"⚠️ Maximum {self.config.max_images_per_pdf} images reached! Please convert current batch first."
                )
            
            # Show options WITHOUT immediate conversion buttons
            keyboard = [
                [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_images_pdf"),
                 InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_images_pdf")],
                [InlineKeyboardButton("📸 Add More Images", callback_data="add_more"),
                 InlineKeyboardButton("🎨 Enhance Images", callback_data="enhance_menu")],
                [InlineKeyboardButton("👁️ Preview Images", callback_data="preview_images"),
                 InlineKeyboardButton("⚙️ Settings", callback_data="conversion_settings")],
                [InlineKeyboardButton("🗑️ Clear All", callback_data="clear_images"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            image_count = len(self.user_data[user_id]['images'])
            await update.message.reply_text(
                f"📸 Image received! ({image_count}/{self.config.max_images_per_pdf} total)\n\nWhat would you like to do?",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error handling photo: {e}")
            await update.message.reply_text("❌ Error processing image. Please try again.")

    async def handle_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """PDF handling with proper file path management"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        try:
            doc = update.message.document
            
            # Check file size
            if doc.file_size and doc.file_size > self.config.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large! Maximum size is {self.config.max_file_size // (1024*1024)}MB."
                )
                return
            
            # Get PDF info without markdown formatting to avoid entity errors
            filename = doc.file_name or "Unknown"
            file_info = f"📄 PDF Received\n\n"
            file_info += f"📁 Name: {filename}\n"
            file_info += f"📏 Size: {(doc.file_size or 0) / (1024*1024):.2f} MB"
            
            # Better button layout with custom naming
            keyboard = [
                [InlineKeyboardButton("🖼️ Convert to Images", callback_data="convert_pdf_images"),
                 InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_pdf_images")],
                [InlineKeyboardButton("📊 PDF Info", callback_data="pdf_info"),
                 InlineKeyboardButton("🔍 Extract Text", callback_data="extract_text")],
                [InlineKeyboardButton("⚙️ Settings", callback_data="pdf_settings"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store PDF info
            self.user_data[user_id]['current_pdf'] = doc
            self.user_data[user_id]['files_processed'] += 1
            self.user_data[user_id]['last_used'] = datetime.now().isoformat()
            
            # Send without markdown to avoid entity parsing errors
            await update.message.reply_text(
                file_info,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error handling PDF: {e}")
            await update.message.reply_text("❌ Error processing PDF. Please try again.")

    async def handle_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Word document handling with proper file path management"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        try:
            doc = update.message.document
            
            # Check file size
            if doc.file_size and doc.file_size > self.config.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large! Maximum size is {self.config.max_file_size // (1024*1024)}MB."
                )
                return
            
            # Better button layout
            keyboard = [
                [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_word_pdf"),
                 InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_word_pdf")],
                [InlineKeyboardButton("📊 Document Info", callback_data="word_info"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            self.user_data[user_id]['current_word'] = doc
            self.user_data[user_id]['files_processed'] += 1
            self.user_data[user_id]['last_used'] = datetime.now().isoformat()
            
            await update.message.reply_text(
                "📝 Word document received! Ready to convert?",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error handling Word document: {e}")
            await update.message.reply_text("❌ Error processing Word document. Please try again.")

    async def handle_excel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Excel file handling with proper file path management"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        try:
            doc = update.message.document
            
            # Check file size
            if doc.file_size and doc.file_size > self.config.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large! Maximum size is {self.config.max_file_size // (1024*1024)}MB."
                )
                return
            
            # Better button layout
            keyboard = [
                [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_excel_pdf"),
                 InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_excel_pdf")],
                [InlineKeyboardButton("📊 Excel Info", callback_data="excel_info"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            self.user_data[user_id]['current_excel'] = doc
            self.user_data[user_id]['files_processed'] += 1
            self.user_data[user_id]['last_used'] = datetime.now().isoformat()
            
            await update.message.reply_text(
                "📊 Excel file received! Ready to convert with enhanced formatting?",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error handling Excel file: {e}")
            await update.message.reply_text("❌ Error processing Excel file. Please try again.")

    async def handle_text_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Text document handling"""
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        try:
            doc = update.message.document
            
            # Check file size
            if doc.file_size and doc.file_size > self.config.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large! Maximum size is {self.config.max_file_size // (1024*1024)}MB."
                )
                return
            
            # Better button layout
            keyboard = [
                [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_text_pdf"),
                 InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_text_pdf")],
                [InlineKeyboardButton("📊 Text Info", callback_data="text_info"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            self.user_data[user_id]['current_text'] = doc
            self.user_data[user_id]['files_processed'] += 1
            self.user_data[user_id]['last_used'] = datetime.now().isoformat()
            
            await update.message.reply_text(
                "📝 Text document received! Ready to convert?",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error handling text document: {e}")
            await update.message.reply_text("❌ Error processing text document. Please try again.")

    async def handle_document_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image documents (non-photo) with proper file path management"""
        user_id = update.effective_user.id
        self._initialize_user_data(user_id)
        
        try:
            doc = update.message.document
            
            # Check file size
            if doc.file_size and doc.file_size > self.config.max_file_size:
                await update.message.reply_text(
                    f"❌ File too large! Maximum size is {self.config.max_file_size // (1024*1024)}MB."
                )
                return
            
            # Download image document
            file = await context.bot.get_file(doc.file_id)
            user_temp_dir = os.path.join(self.temp_base_dir, str(user_id))
            os.makedirs(user_temp_dir, exist_ok=True)
            
            # Sanitize filename properly
            original_filename = doc.file_name or "image"
            safe_filename = self.security.sanitize_filename(original_filename)
            # Ensure unique filename
            if not safe_filename or safe_filename == "unnamed_file":
                safe_filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
            
            image_path = os.path.join(user_temp_dir, safe_filename)
            
            # Download file
            await file.download_to_drive(image_path)
            
            # Verify file was downloaded
            if not os.path.exists(image_path):
                await update.message.reply_text("❌ Error downloading image. Please try again.")
                return
            
            self.user_data[user_id]['images'].append(image_path)
            self.user_data[user_id]['files_processed'] += 1
            self.user_data[user_id]['last_used'] = datetime.now().isoformat()
            
            keyboard = [
                [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_images_pdf"),
                 InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_images_pdf")],
                [InlineKeyboardButton("🎨 Enhance Image", callback_data="enhance_menu"),
                 InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🖼️ Image document received!\nFormat: {doc.mime_type}",
                reply_markup=reply_markup
            )
        except Exception as e:
            self.logger.error(f"Error handling document image: {e}")
            await update.message.reply_text("❌ Error processing image document.")

    async def handle_other_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle other document types"""
        doc = update.message.document
        file_info = f"📄 Document received: {doc.file_name}\n"
        file_info += f"Type: {doc.mime_type or 'Unknown'}\n"
        file_info += f"Size: {(doc.file_size or 0) / (1024*1024):.2f} MB\n\n"
        file_info += "This file type is not directly supported for conversion, but you can try:\n"
        file_info += "• Save as PDF if possible\n"
        file_info += "• Convert to supported format first\n"
        file_info += "• Use /formats to see supported types"
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(file_info, reply_markup=reply_markup)
