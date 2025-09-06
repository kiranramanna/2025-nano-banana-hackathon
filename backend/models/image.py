"""
Image generation models
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ImageRequest:
    """Image generation request model"""
    story_id: str
    scene_number: int
    custom_prompt: Optional[str] = None
    style: str = 'watercolor'
    aspect_ratio: str = '16:9'
    regenerate: bool = False

@dataclass
class ImageResponse:
    """Image generation response model"""
    image_url: str
    scene_number: int
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self):
        return {
            'image_url': self.image_url,
            'scene_number': self.scene_number,
            'success': self.success,
            'error': self.error
        }