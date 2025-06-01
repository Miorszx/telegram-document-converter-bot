"""
Security and validation utilities for the Telegram Document Converter Bot
"""

import os
import hashlib
import uuid
import re
from typing import List

try:
    import magic  # For file type detection
    MAGIC_AVAILABLE = True
except ImportError:
    magic = None
    MAGIC_AVAILABLE = False
    print("⚠️  python-magic not available. File validation will be limited.")


class SecurityManager:
    """Handle security and validation"""
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        if not filename:
            return False
        
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(char in filename for char in dangerous_chars)
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 100) -> str:
        """Sanitize filename to make it safe while preserving original name"""
        if not filename:
            return "unnamed_file"
        
        # Remove file extension to preserve it separately
        name, ext = os.path.splitext(filename)
        
        # Replace problematic characters but keep spaces and common punctuation
        safe_chars = []
        for char in name:
            if char.isalnum() or char in ' -_.()[]':
                safe_chars.append(char)
            else:
                safe_chars.append('_')
        
        safe_name = ''.join(safe_chars).strip()
        
        # Remove multiple spaces and underscores
        safe_name = re.sub(r'[_\s]+', '_', safe_name)
        safe_name = safe_name.strip('_')
        
        # Ensure we have a name
        if not safe_name:
            safe_name = "file"
        
        # Limit length but preserve extension
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]
        
        # Return with original extension
        return safe_name + ext
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Generate hash for file deduplication"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return str(uuid.uuid4())
    
    @staticmethod
    def validate_file_type(file_path: str, expected_types: List[str]) -> bool:
        """Validate file type - Fixed to be less strict"""
        try:
            # Always return True if magic is not available
            if not MAGIC_AVAILABLE:
                # Fallback to extension checking
                ext = os.path.splitext(file_path)[1].lower()
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
                if 'image' in expected_types:
                    return ext in image_extensions
                return True
            
            file_type = magic.from_file(file_path, mime=True)
            return any(expected in file_type for expected in expected_types)
        except Exception:
            # If validation fails, be permissive
            return True
    
    @staticmethod
    def escape_markdown_v2(text: str) -> str:
        """Escape special characters for Telegram MarkdownV2"""
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
