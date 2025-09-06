"""
Export request models
"""

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ExportRequest:
    """Export request model"""
    story_id: str
    format: str  # 'pdf', 'html', 'json', 'epub'
    images: Dict[str, str]
    filename: Optional[str] = None
    include_images: bool = True
    include_metadata: bool = True