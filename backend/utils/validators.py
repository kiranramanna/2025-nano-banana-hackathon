"""
Request validation utilities
"""

from typing import Dict, List, Any, Optional

def validate_story_request(data: Dict[str, Any]) -> Optional[List[str]]:
    """Validate story generation request"""
    errors = []
    
    # Required fields
    if not data.get('prompt'):
        errors.append("'prompt' is required")
    elif len(data['prompt'].strip()) < 10:
        errors.append("'prompt' must be at least 10 characters long")
    
    # Optional fields validation
    age_group = data.get('age_group')
    if age_group and age_group not in ['3-6', '7-10', '11-14', '15+']:
        errors.append("Invalid age_group. Must be one of: 3-6, 7-10, 11-14, 15+")
    
    genre = data.get('genre')
    valid_genres = ['adventure', 'fantasy', 'science-fiction', 'mystery', 'comedy', 'educational']
    if genre and genre not in valid_genres:
        errors.append(f"Invalid genre. Must be one of: {', '.join(valid_genres)}")
    
    num_scenes = data.get('num_scenes')
    if num_scenes is not None:
        try:
            num = int(num_scenes)
            if num < 3 or num > 10:
                errors.append("num_scenes must be between 3 and 10")
        except (ValueError, TypeError):
            errors.append("num_scenes must be a number")
    
    art_style = data.get('art_style')
    valid_styles = ['watercolor', 'cartoon', 'pixel-art', 'anime', 'realistic', 'sketch']
    if art_style and art_style not in valid_styles:
        errors.append(f"Invalid art_style. Must be one of: {', '.join(valid_styles)}")
    
    return errors if errors else None

def validate_image_request(data: Dict[str, Any]) -> Optional[List[str]]:
    """Validate image generation request"""
    errors = []
    
    # Required fields
    if not data.get('story_id'):
        errors.append("'story_id' is required")
    
    scene_number = data.get('scene_number')
    if scene_number is None:
        errors.append("'scene_number' is required")
    else:
        try:
            num = int(scene_number)
            if num < 1:
                errors.append("scene_number must be positive")
        except (ValueError, TypeError):
            errors.append("scene_number must be a number")
    
    # Optional fields
    aspect_ratio = data.get('aspect_ratio')
    valid_ratios = ['16:9', '9:16', '1:1', '4:3', '3:4']
    if aspect_ratio and aspect_ratio not in valid_ratios:
        errors.append(f"Invalid aspect_ratio. Must be one of: {', '.join(valid_ratios)}")
    
    custom_prompt = data.get('custom_prompt')
    if custom_prompt and len(custom_prompt.strip()) < 10:
        errors.append("custom_prompt must be at least 10 characters long")
    
    return errors if errors else None

def validate_export_request(data: Dict[str, Any]) -> Optional[List[str]]:
    """Validate export request"""
    errors = []
    
    # Required fields
    if not data.get('story_id'):
        errors.append("'story_id' is required")
    
    format_type = data.get('format')
    valid_formats = ['pdf', 'html', 'json', 'epub']
    if not format_type:
        errors.append("'format' is required")
    elif format_type not in valid_formats:
        errors.append(f"Invalid format. Must be one of: {', '.join(valid_formats)}")
    
    # Optional validation
    images = data.get('images')
    if images and not isinstance(images, dict):
        errors.append("'images' must be a dictionary/object")
    
    filename = data.get('filename')
    if filename:
        # Check for invalid characters
        invalid_chars = ['/', '\\', '..', '<', '>', '|', ':', '*', '?', '"']
        for char in invalid_chars:
            if char in filename:
                errors.append(f"Filename contains invalid character: {char}")
                break
    
    return errors if errors else None

def validate_character_update(data: Dict[str, Any]) -> Optional[List[str]]:
    """Validate character update request"""
    errors = []
    
    if not data.get('story_id'):
        errors.append("'story_id' is required")
    
    if not data.get('character_name'):
        errors.append("'character_name' is required")
    
    updates = data.get('updates')
    if not updates or not isinstance(updates, dict):
        errors.append("'updates' must be a non-empty dictionary")
    
    # Validate update fields
    valid_fields = ['description', 'visual_description', 'refined_description', 'role']
    if updates:
        for field in updates.keys():
            if field not in valid_fields:
                errors.append(f"Invalid update field: {field}")
    
    return errors if errors else None