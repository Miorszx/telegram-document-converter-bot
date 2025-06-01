"""
Conversation handlers for custom naming functionality
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from utils.security import SecurityManager

# Conversation states
WAITING_FOR_NAME = 1


class ConversationHandlers:
    """Handles conversation flows like custom naming"""
    
    def __init__(self, user_data: dict, security: SecurityManager):
        self.user_data = user_data
        self.security = security
        self.logger = logging.getLogger(__name__)
    
    async def start_custom_naming(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start custom naming conversation"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Extract conversion type from callback data
        conversion_type = query.data.replace('custom_name_', '')
        self.user_data[user_id]['pending_conversion'] = conversion_type
        
        await query.edit_message_text(
            "📝 *Custom Filename*\n\n"
            "Please send the custom filename you want to use.\n"
            "Don't include the file extension (.pdf, .zip etc.) - I'll add it automatically!\n\n"
            "Type /cancel to go back to conversion options.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_FOR_NAME
    
    async def receive_custom_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive custom name from user"""
        user_id = update.effective_user.id
        custom_name = update.message.text.strip()
        
        # Sanitize the filename
        safe_name = self.security.sanitize_filename(custom_name + ".tmp").replace(".tmp", "")
        
        if not safe_name or safe_name == "unnamed_file":
            await update.message.reply_text(
                "❌ Invalid filename! Please try again with a valid name.\n"
                "Use letters, numbers, spaces, dots, hyphens and underscores only."
            )
            return WAITING_FOR_NAME
        
        # Store custom filename
        self.user_data[user_id]['custom_filename'] = safe_name
        
        # Get pending conversion type
        conversion_type = self.user_data[user_id].get('pending_conversion')
        
        await update.message.reply_text(f"✅ Custom filename set: `{safe_name}`\n\n🔄 Starting conversion...", 
                                      parse_mode=ParseMode.MARKDOWN)
        
        # Store conversion info for the main bot to handle
        self.user_data[user_id]['execute_conversion'] = conversion_type
        
        # Clear pending conversion data
        self.user_data[user_id]['pending_conversion'] = None
        
        return ConversationHandler.END
    
    async def cancel_naming(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel custom naming"""
        user_id = update.effective_user.id
        if user_id in self.user_data:
            self.user_data[user_id]['pending_conversion'] = None
            self.user_data[user_id]['custom_filename'] = None
        
        await update.message.reply_text("❌ Custom naming cancelled.")
        return ConversationHandler.END
