"""
Callback handlers for inline keyboard interactions
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.config import BotConfig
from utils.security import SecurityManager


class CallbackHandlers:
    """Handles all callback query interactions"""
    
    def __init__(self, config: BotConfig, user_data: dict, security: SecurityManager):
        self.config = config
        self.user_data = user_data
        self.security = security
        self.logger = logging.getLogger(__name__)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced callback handling with all buttons working"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        try:
            # Route callbacks to appropriate handlers
            if data.startswith("convert_"):
                await self.handle_conversion_callbacks(query, context, data)
            elif data.startswith("enhance_"):
                await self.handle_enhancement_callbacks(query, context, data)
            elif data.startswith("setting_") or data.startswith("quality_") or data.startswith("format_"):
                await self.handle_settings_callbacks(query, context, data)
            elif data.startswith("show_"):
                await self.handle_show_callbacks(query, context, data)
            else:
                await self.handle_general_callbacks(query, context, data)
                
        except Exception as e:
            self.logger.error(f"Error in callback handler for user {user_id}, data: {data}: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")

    async def handle_conversion_callbacks(self, query, context, data):
        """Handle conversion-related callbacks"""
        # Store the conversion request for the main bot to handle
        user_id = query.from_user.id
        conversion_type = data.replace('convert_', '')
        self.user_data[user_id]['requested_conversion'] = conversion_type
        
        await query.edit_message_text("🔄 Conversion requested! Processing...")

    async def handle_enhancement_callbacks(self, query, context, data):
        """Handle image enhancement callbacks"""
        if data == "enhance_menu":
            keyboard = [
                [InlineKeyboardButton("🔆 Brightness", callback_data="enhance_brightness"),
                 InlineKeyboardButton("🌟 Contrast", callback_data="enhance_contrast")],
                [InlineKeyboardButton("📏 Sharpness", callback_data="enhance_sharpness"),
                 InlineKeyboardButton("🎨 Auto Enhance", callback_data="enhance_auto")],
                [InlineKeyboardButton("⚫ Grayscale", callback_data="enhance_grayscale"),
                 InlineKeyboardButton("🔙 Back", callback_data="back_to_images")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🎨 Choose enhancement type:",
                reply_markup=reply_markup
            )
        elif data.startswith("enhance_"):
            enhancement_type = data.replace("enhance_", "")
            user_id = query.from_user.id
            self.user_data[user_id]['requested_enhancement'] = enhancement_type
            await query.edit_message_text(f"🎨 {enhancement_type.title()} enhancement requested!")

    async def handle_settings_callbacks(self, query, context, data):
        """Handle settings callbacks including quality selection"""
        user_id = query.from_user.id
        
        if data == "setting_quality":
            # Show quality selection menu
            current_quality = self.user_data[user_id]['settings'].get('quality', 'medium')
            
            keyboard = [
                [InlineKeyboardButton(f"📉 Low {'✅' if current_quality == 'low' else ''}", callback_data="quality_low"),
                 InlineKeyboardButton(f"📊 Medium {'✅' if current_quality == 'medium' else ''}", callback_data="quality_medium")],
                [InlineKeyboardButton(f"📈 High {'✅' if current_quality == 'high' else ''}", callback_data="quality_high"),
                 InlineKeyboardButton(f"🚀 Ultra {'✅' if current_quality == 'ultra' else ''}", callback_data="quality_ultra")],
                [InlineKeyboardButton("🔙 Back to Settings", callback_data="show_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            quality_info = f"""
📸 *Select Image Quality*

Current: *{current_quality.title()}*

📉 *Low (72 DPI)*
• Fastest processing
• Smallest file size
• Basic quality

📊 *Medium (150 DPI)*
• Balanced speed/quality
• Good for most uses
• Recommended default

📈 *High (300 DPI)*
• Higher quality
• Larger file size
• Better for printing

🚀 *Ultra (600 DPI)*
• Maximum quality
• Largest file size
• Professional quality
            """
            
            await query.edit_message_text(
                quality_info,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        elif data == "setting_format":
            current_format = self.user_data[user_id]['settings'].get('format', 'PNG')
            
            keyboard = [
                [InlineKeyboardButton(f"PNG {'✅' if current_format == 'PNG' else ''}", callback_data="format_PNG"),
                 InlineKeyboardButton(f"JPEG {'✅' if current_format == 'JPEG' else ''}", callback_data="format_JPEG")],
                [InlineKeyboardButton("🔙 Back to Settings", callback_data="show_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🖼️ *Select Output Format*\n\nCurrent: *{current_format}*\n\n• PNG: Lossless, larger files\n• JPEG: Compressed, smaller files",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        elif data == "setting_auto_enhance":
            current = self.user_data[user_id]['settings'].get('auto_enhance', False)
            self.user_data[user_id]['settings']['auto_enhance'] = not current
            status = "Enabled" if not current else "Disabled"
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Settings", callback_data="show_settings")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✨ *Auto-enhance {status}!*\n\nImages will be {'automatically enhanced' if not current else 'converted without enhancement'} before PDF conversion.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        elif data.startswith("quality_"):
            quality = data.replace("quality_", "")
            self.user_data[user_id]['settings']['quality'] = quality
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Settings", callback_data="show_settings"),
                 InlineKeyboardButton("📄 Convert Images Now", callback_data="convert_images_pdf")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📸 *Quality set to {quality.title()}!*\n\nThis setting will be used for all future conversions.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        elif data.startswith("format_"):
            format_type = data.replace("format_", "")
            self.user_data[user_id]['settings']['format'] = format_type
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Settings", callback_data="show_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🖼️ *Format set to {format_type}!*\n\nThis will be used for PDF to images conversion.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

    async def handle_show_callbacks(self, query, context, data):
        """Handle show callbacks"""
        if data == "show_help":
            await self.show_help_inline(query)
        elif data == "show_stats":
            await self.show_stats_inline(query)
        elif data == "show_settings":
            await self.show_settings_inline(query)
        elif data == "show_formats":
            await self.show_formats_inline(query)

    async def handle_general_callbacks(self, query, context, data):
        """Handle general callbacks"""
        user_id = query.from_user.id
        
        if data == "clear_session":
            await self.clear_session_inline(query)
        elif data == "clear_images":
            if user_id in self.user_data:
                self.user_data[user_id]['images'] = []
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🗑️ Images cleared! Send new images to start over.",
                reply_markup=reply_markup
            )
        elif data == "add_more":
            await query.edit_message_text("📸 Send more images to add to your collection!")
        elif data == "preview_images":
            await self.preview_images(query, context)
        elif data == "conversion_settings":
            await self.show_conversion_settings(query)
        elif data == "back_to_main":
            await self.show_main_menu(query)
        elif data == "back_to_images":
            await self.show_image_menu(query)
        elif data in ["pdf_info", "word_info", "excel_info", "text_info"]:
            info_type = data.replace("_info", "")
            self.user_data[user_id]['requested_info'] = info_type
            await query.edit_message_text(f"📊 {info_type.title()} info requested!")
        elif data == "pdf_settings":
            await self.show_pdf_settings(query)
        elif data == "extract_text":
            self.user_data[user_id]['requested_action'] = 'extract_text'
            await query.edit_message_text("🔍 Text extraction requested!")

    # Inline display methods
    async def show_help_inline(self, query):
        """Show help inline"""
        help_text = """
📚 *Quick Help*

📸 *Images:* Send photos → Convert to PDF
📄 *PDFs:* Send PDF → Extract as images
📝 *Documents:* Send DOCX/XLSX → Convert to PDF
📝 *Custom Names:* Click "📝 Custom Name" before converting

*Commands:*
/start - Main menu
/help - Detailed help
/stats - Your statistics
/settings - Preferences
/clear - Clear session
/cancel - Cancel custom naming

*Tips:* Send multiple images for batch conversion!
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_stats_inline(self, query):
        """Show stats inline"""
        user_id = query.from_user.id
        stats = self.user_data[user_id]
        
        stats_text = f"""
📊 *Your Statistics*

🔄 Conversions: {stats.get('conversions', 0)}
📁 Files Processed: {stats.get('files_processed', 0)}
📸 Images in Queue: {len(stats.get('images', []))}

🏆 Keep converting!
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_settings_inline(self, query):
        """Show settings inline"""
        user_id = query.from_user.id
        settings = self.user_data[user_id]['settings']
        
        settings_text = f"""
🎛️ *Current Settings*

📸 Quality: *{settings.get('quality', 'medium').title()}*
🖼️ Format: *{settings.get('format', 'PNG')}*
✨ Auto-Enhance: *{'On' if settings.get('auto_enhance', False) else 'Off'}*

Click below to change settings:
        """
        
        keyboard = [
            [InlineKeyboardButton("📸 Quality", callback_data="setting_quality"),
             InlineKeyboardButton("🖼️ Format", callback_data="setting_format")],
            [InlineKeyboardButton("✨ Auto-Enhance", callback_data="setting_auto_enhance")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_formats_inline(self, query):
        """Show formats inline"""
        formats_text = """
📋 *Supported Formats*

📸 *Images:* JPG, PNG, GIF, BMP, TIFF → PDF
📄 *Documents:* PDF ↔ Images
📝 *Word:* DOCX, DOC → PDF
📊 *Excel:* XLSX, XLS → PDF (Enhanced!)
📄 *Text:* TXT, HTML, MD → PDF

*Max file size:* 50MB
*Max images per PDF:* 50

✨ *New:* Custom filenames supported!
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            formats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def clear_session_inline(self, query):
        """Clear session inline"""
        user_id = query.from_user.id
        if user_id in self.user_data:
            current_data = self.user_data[user_id]
            self.user_data[user_id]['images'] = []
            # Clear temporary document references
            for key in ['current_pdf', 'current_word', 'current_excel', 'current_text', 'pending_conversion', 'custom_filename']:
                if key in current_data:
                    del current_data[key]
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🧹 Session cleared! Ready for new conversions!",
            reply_markup=reply_markup
        )

    async def show_main_menu(self, query):
        """Show main menu"""
        welcome_text = """
🚀 *Advanced Document Converter*

Ready to convert your files!

Send me any supported file to get started.
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 Help", callback_data="show_help"),
             InlineKeyboardButton("🎛️ Settings", callback_data="show_settings")],
            [InlineKeyboardButton("📊 Stats", callback_data="show_stats"),
             InlineKeyboardButton("📋 Formats", callback_data="show_formats")],
            [InlineKeyboardButton("🧹 Clear Session", callback_data="clear_session")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_image_menu(self, query):
        """Show image menu"""
        user_id = query.from_user.id
        image_count = len(self.user_data[user_id]['images'])
        
        text = f"📸 Images in queue: {image_count}\n\nWhat would you like to do?"
        
        keyboard = [
            [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_images_pdf"),
             InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_images_pdf")],
            [InlineKeyboardButton("📸 Add More", callback_data="add_more"),
             InlineKeyboardButton("🎨 Enhance", callback_data="enhance_menu")],
            [InlineKeyboardButton("👁️ Preview", callback_data="preview_images"),
             InlineKeyboardButton("⚙️ Settings", callback_data="conversion_settings")],
            [InlineKeyboardButton("🗑️ Clear All", callback_data="clear_images"),
             InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)

    async def preview_images(self, query, context):
        """Preview images in queue"""
        user_id = query.from_user.id
        images = self.user_data[user_id].get('images', [])
        
        if not images:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📸 No images in queue.",
                reply_markup=reply_markup
            )
            return
        
        preview_text = f"👁️ *Image Preview*\n\n"
        preview_text += f"Total images: {len(images)}\n\n"
        
        for i, img_path in enumerate(images[:5], 1):  # Show first 5
            filename = os.path.basename(img_path)
            try:
                size = os.path.getsize(img_path) / 1024  # KB
                preview_text += f"{i}. {filename} ({size:.1f} KB)\n"
            except:
                preview_text += f"{i}. {filename}\n"
        
        if len(images) > 5:
            preview_text += f"... and {len(images) - 5} more"
        
        keyboard = [
            [InlineKeyboardButton("📄 Convert to PDF", callback_data="convert_images_pdf"),
             InlineKeyboardButton("📝 Custom Name", callback_data="custom_name_images_pdf")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_images")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            preview_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_conversion_settings(self, query):
        """Show conversion settings"""
        user_id = query.from_user.id
        settings = self.user_data[user_id]['settings']
        
        text = f"""
⚙️ *Conversion Settings*

Current settings for your conversions:

📸 Quality: *{settings.get('quality', 'medium').title()}*
🖼️ Format: *{settings.get('format', 'PNG')}*
✨ Auto-Enhance: *{'On' if settings.get('auto_enhance', False) else 'Off'}*

Change settings before converting:
        """
        
        keyboard = [
            [InlineKeyboardButton("📸 Quality", callback_data="setting_quality"),
             InlineKeyboardButton("🖼️ Format", callback_data="setting_format")],
            [InlineKeyboardButton("✨ Auto-Enhance", callback_data="setting_auto_enhance")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_images")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_pdf_settings(self, query):
        """Show PDF conversion settings"""
        user_id = query.from_user.id
        settings = self.user_data[user_id]['settings']
        
        text = f"""
⚙️ *PDF Conversion Settings*

📸 Quality: *{settings.get('quality', 'medium').title()}*
🖼️ Format: *{settings.get('format', 'PNG')}*

These settings will be used for PDF to images conversion.
        """
        
        keyboard = [
            [InlineKeyboardButton("📸 Change Quality", callback_data="setting_quality"),
             InlineKeyboardButton("🖼️ Change Format", callback_data="setting_format")],
            [InlineKeyboardButton("🔙 Back", callback_data="convert_pdf_images")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
