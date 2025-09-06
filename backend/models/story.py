"""
Story data models
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Character:
    """Character model"""
    name: str
    description: str
    visual_description: str
    role: str = 'supporting'
    refined_description: Optional[str] = None
    character_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'visual_description': self.visual_description,
            'role': self.role,
            'refined_description': self.refined_description,
            'character_id': self.character_id
        }

@dataclass
class Scene:
    """Scene model"""
    scene_number: int
    title: str
    text: str
    image_prompt: str
    characters_present: List[str]
    image_url: Optional[str] = None
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {
            'scene_number': self.scene_number,
            'title': self.title,
            'text': self.text,
            'image_prompt': self.image_prompt,
            'characters_present': self.characters_present,
            'image_url': self.image_url,
            'scene_id': self.scene_id
        }

@dataclass
class Story:
    """Story model"""
    title: str
    characters: List[Character]
    scenes: List[Scene]
    style: str = 'watercolor'
    age_group: str = '7-10'
    genre: str = 'adventure'
    total_planned_scenes: int = 5
    story_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'title': self.title,
            'characters': [c.to_dict() for c in self.characters],
            'scenes': [s.to_dict() for s in self.scenes],
            'style': self.style,
            'age_group': self.age_group,
            'genre': self.genre,
            'total_planned_scenes': self.total_planned_scenes,
            'story_id': self.story_id,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create Story from dictionary"""
        characters = [Character(**c) if isinstance(c, dict) else c 
                     for c in data.get('characters', [])]
        scenes = [Scene(**s) if isinstance(s, dict) else s 
                 for s in data.get('scenes', [])]
        
        return cls(
            title=data.get('title', 'Untitled'),
            characters=characters,
            scenes=scenes,
            style=data.get('style', 'watercolor'),
            age_group=data.get('age_group', '7-10'),
            genre=data.get('genre', 'adventure'),
            total_planned_scenes=data.get('total_planned_scenes', 5),
            story_id=data.get('story_id', str(uuid.uuid4()))
        )