"""
Cache service for storing stories and images
"""

import json
import os
import logging
from typing import Optional, Dict, List
from datetime import datetime
from models.story import Story
from config import config

logger = logging.getLogger(__name__)

_GLOBAL_STORIES: Dict[str, Story] = {}
_GLOBAL_CHARACTERS: Dict[str, dict] = {}
_CACHE_LOADED = False


class CacheService:
    """In-memory and file-based cache for stories"""
    
    def __init__(self):
        global _CACHE_LOADED
        # Use module-level shared dictionaries so all service instances share cache
        self.stories = _GLOBAL_STORIES
        self.characters = _GLOBAL_CHARACTERS
        # Load from disk only once per process
        if not _CACHE_LOADED:
            self._load_from_disk()
            _CACHE_LOADED = True
    
    def store_story(self, story: Story) -> bool:
        """Store story in cache and disk"""
        try:
            # Store in memory
            self.stories[story.story_id] = story
            
            # Store characters
            for char in story.characters:
                char_key = f"{story.story_id}_{char.name.replace(' ', '_')}"
                self.characters[char_key] = char.to_dict()
            
            # Save to disk
            self._save_to_disk(story)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache story: {e}")
            return False
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """Retrieve story from cache"""
        return self.stories.get(story_id)
    
    def get_character(self, story_id: str, character_name: str) -> Optional[dict]:
        """Retrieve character data"""
        char_key = f"{story_id}_{character_name.replace(' ', '_')}"
        return self.characters.get(char_key)
    
    def list_stories(self) -> List[Dict]:
        """List all cached stories"""
        stories_list = []
        for story_id, story in self.stories.items():
            stories_list.append({
                'id': story_id,
                'title': story.title,
                'num_scenes': len(story.scenes),
                'created_at': story.created_at.isoformat(),
                'genre': story.genre,
                'age_group': story.age_group
            })
        
        # Sort by creation date (newest first)
        stories_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        return stories_list
    
    def delete_story(self, story_id: str) -> bool:
        """Delete story from cache"""
        try:
            if story_id in self.stories:
                # Remove from memory
                story = self.stories.pop(story_id)
                
                # Remove characters
                for char in story.characters:
                    char_key = f"{story_id}_{char.name.replace(' ', '_')}"
                    self.characters.pop(char_key, None)
                
                # Remove from disk
                filepath = os.path.join(
                    config.STORY_FOLDER, 
                    f"{story_id}.json"
                )
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete story: {e}")
            return False
    
    def _save_to_disk(self, story: Story):
        """Save story to disk as JSON"""
        try:
            filepath = os.path.join(
                config.STORY_FOLDER,
                f"{story.story_id}.json"
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(story.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Story saved to disk: {story.story_id}")
            
        except Exception as e:
            logger.error(f"Failed to save story to disk: {e}")
    
    def _load_from_disk(self):
        """Load all stories from disk on startup"""
        try:
            if not os.path.exists(config.STORY_FOLDER):
                return
            
            for filename in os.listdir(config.STORY_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(config.STORY_FOLDER, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    story = Story.from_dict(data)
                    self.stories[story.story_id] = story
                    
                    # Load characters
                    for char in story.characters:
                        char_key = f"{story.story_id}_{char.name.replace(' ', '_')}"
                        self.characters[char_key] = char.to_dict()
            
            logger.info(f"Loaded {len(self.stories)} stories from disk")
            
        except Exception as e:
            logger.error(f"Failed to load stories from disk: {e}")
    
    def clear_cache(self):
        """Clear all cached data (for testing)"""
        self.stories.clear()
        self.characters.clear()
        # Also reset disk state is intentionally not performed here
        logger.info("Cache cleared")
