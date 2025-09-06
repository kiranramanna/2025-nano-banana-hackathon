"""
Helper utility functions
"""

import re
import uuid
from datetime import datetime
from typing import Optional
import hashlib
import os

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for safe file system storage
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename

def generate_unique_id(prefix: Optional[str] = None) -> str:
    """
    Generate a unique identifier with optional prefix
    """
    unique_id = str(uuid.uuid4())
    
    if prefix:
        return f"{prefix}_{unique_id}"
    
    return unique_id

def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Format timestamp for filenames or display
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime(format_str)

def get_file_hash(filepath: str) -> str:
    """
    Calculate MD5 hash of a file
    """
    hash_md5 = hashlib.md5()
    
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes
    """
    word_count = len(text.split())
    reading_time = word_count / words_per_minute
    
    # Round up to nearest minute
    return max(1, int(reading_time + 0.5))

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"

def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """
    Extract keywords from text (simple implementation)
    """
    # Remove common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
    }
    
    # Convert to lowercase and split
    words = text.lower().split()
    
    # Count word frequency
    word_freq = {}
    for word in words:
        # Clean word
        word = re.sub(r'[^a-z0-9]', '', word)
        
        if word and word not in stop_words and len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, _ in sorted_words[:max_keywords]]