"""
Story generation and management service
"""

import logging
from typing import Optional, Dict, List
from models.story import Story, Scene, Character
from .gemini_client import GeminiClient
from .cache_service import CacheService

logger = logging.getLogger(__name__)

class StoryService:
    """Service for story generation and management"""
    
    def __init__(self):
        self.gemini = GeminiClient()
        self.cache = CacheService()
    
    def generate_story(self,
                      prompt: str,
                      age_group: str = '7-10',
                      genre: str = 'adventure',
                      num_scenes: int = 5,
                      art_style: str = 'watercolor') -> Story:
        """Generate initial story setup with only first 2 scenes"""
        
        logger.info(f"Generating story for prompt: {prompt[:50]}...")
        
        # Generate only the initial 2 scenes to start
        system_prompt = self._build_initial_story_prompt(age_group, genre, num_scenes)
        
        try:
            story_data = self.gemini.generate_json(
                prompt=f"Story prompt: {prompt}",
                system_prompt=system_prompt
            )
            
            story = self._parse_story_data(story_data)
            story.age_group = age_group
            story.genre = genre
            story.style = art_style
            story.total_planned_scenes = num_scenes  # Store total scenes for later
            
            # Cache the story
            self.cache.store_story(story)
            
            return story
            
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            raise
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """Retrieve story by ID"""
        return self.cache.get_story(story_id)
    
    def list_stories(self) -> List[Dict]:
        """List all cached stories"""
        return self.cache.list_stories()
    
    def update_character(self,
                        story_id: str,
                        character_name: str,
                        updates: Dict) -> bool:
        """Update character details"""
        story = self.get_story(story_id)
        if not story:
            return False
        
        for char in story.characters:
            if char.name == character_name:
                for key, value in updates.items():
                    if hasattr(char, key):
                        setattr(char, key, value)
                self.cache.store_story(story)
                return True
        
        return False
    
    def _build_initial_story_prompt(self, age_group: str, genre: str, total_scenes: int) -> str:
        """Build the system prompt for initial story generation (only first scene)"""
        return f"""
        You are a creative children's story writer. Generate the OPENING of a story suitable for {age_group} year olds.
        Genre: {genre}
        
        IMPORTANT: Generate ONLY the first scene to establish the story. The story will eventually have {total_scenes} scenes total,
        but ALL remaining scenes will be created dynamically based on reader choices.
        
        Return the story setup in JSON format with the following structure:
        {{
            "title": "Story Title",
            "characters": [
                {{
                    "name": "Character Name",
                    "description": "Physical appearance and personality",
                    "visual_description": "Detailed visual description for image generation",
                    "role": "main/supporting"
                }}
            ],
            "scenes": [
                {{
                    "scene_number": 1,
                    "title": "Opening Scene Title",
                    "text": "Opening scene narrative text (2-3 paragraphs) that sets up the story",
                    "image_prompt": "Detailed description for image generation",
                    "characters_present": ["Character names in this scene"]
                }}
            ],
            "style": "Art style description"
        }}
        
        Guidelines:
        - Generate ONLY ONE scene (the opening scene)
        - Keep language age-appropriate  
        - Include vivid descriptions for visual generation
        - Create an engaging opening that hooks the reader
        - Set up the story premise clearly
        - Remember: generate exactly 1 scene, not more
        """
    
    def _parse_story_data(self, data: Dict) -> Story:
        """Parse JSON data into Story object"""
        characters = []
        for char_data in data.get('characters', []):
            characters.append(Character(
                name=char_data['name'],
                description=char_data['description'],
                visual_description=char_data['visual_description'],
                role=char_data.get('role', 'supporting')
            ))
        
        scenes = []
        for scene_data in data.get('scenes', []):
            scenes.append(Scene(
                scene_number=scene_data['scene_number'],
                title=scene_data['title'],
                text=scene_data['text'],
                image_prompt=scene_data['image_prompt'],
                characters_present=scene_data.get('characters_present', [])
            ))
        
        return Story(
            title=data.get('title', 'Untitled Story'),
            characters=characters,
            scenes=scenes,
            style=data.get('style', 'watercolor')
        )
    
    def generate_story_choices(self,
                               current_scene: Dict,
                               genre: str = 'adventure',
                               age_group: str = '7-10') -> List[Dict]:
        """Generate 4 different story branching choices"""
        
        logger.info("Generating story choices for next scene")
        
        prompt = f"""
        Based on this current scene: {current_scene.get('content', '')}
        
        Generate 4 different story path choices for what happens next.
        Genre: {genre}
        Age group: {age_group}
        
        Return JSON with this structure:
        [
            {{
                "title": "Original Path",
                "description": "Continue with the main storyline",
                "icon": "📖",
                "type": "original",
                "preview": "Brief preview of what happens if this choice is selected"
            }},
            {{
                "title": "Magical Twist",
                "description": "Add a magical element",
                "icon": "✨",
                "type": "magical",
                "preview": "Brief preview"
            }},
            {{
                "title": "Surprise Turn",
                "description": "Unexpected twist",
                "icon": "🎭",
                "type": "surprise",
                "preview": "Brief preview"
            }},
            {{
                "title": "Adventure Path",
                "description": "New adventure",
                "icon": "🚀",
                "type": "adventure",
                "preview": "Brief preview"
            }}
        ]
        
        Make the first choice follow the original story path, and make the other three creative alternatives.
        Keep descriptions brief and age-appropriate.
        """
        
        try:
            choices = self.gemini.generate_json(
                prompt=prompt,
                system_prompt="Generate story branching choices"
            )
            return choices if isinstance(choices, list) else []
        except Exception as e:
            logger.error(f"Failed to generate choices: {e}")
            # Return default choices
            return [
                {
                    "title": "Original Path",
                    "description": "Continue with the main storyline",
                    "icon": "📖",
                    "type": "original"
                },
                {
                    "title": "Magical Twist",
                    "description": "Add a magical element to the story",
                    "icon": "✨",
                    "type": "magical"
                },
                {
                    "title": "Surprise Turn",
                    "description": "Introduce an unexpected twist",
                    "icon": "🎭",
                    "type": "surprise"
                },
                {
                    "title": "Adventure Path",
                    "description": "Take the story on an adventure",
                    "icon": "🚀",
                    "type": "adventure"
                }
            ]
    
    def _summarize_scenes(self, scenes: List[Scene]) -> str:
        """Create a brief summary of existing scenes"""
        summary = []
        for scene in scenes:
            summary.append(f"Scene {scene.scene_number}: {scene.title} - {scene.text[:100]}...")
        return "\n".join(summary)
    
    def generate_scene_from_choice(self,
                                   story_id: str,
                                   choice: Dict,
                                   genre: str = 'adventure',
                                   age_group: str = '7-10',
                                   art_style: str = 'watercolor') -> Optional[Dict]:
        """Generate a new scene based on the selected choice"""
        
        logger.info(f"Generating scene for choice: {choice.get('title')}")
        
        story = self.get_story(story_id)
        if not story:
            logger.error(f"Story {story_id} not found")
            return None
        
        # Calculate remaining scenes
        current_scene_count = len(story.scenes)
        total_planned = getattr(story, 'total_planned_scenes', 5)
        remaining_scenes = total_planned - current_scene_count
        
        # Get character descriptions for consistency
        character_info = "\n".join([
            f"- {char.name}: {char.visual_description}"
            for char in story.characters
        ])
        
        # Summarize previous scenes
        scenes_summary = self._summarize_scenes(story.scenes)
        
        prompt = f"""
        Story title: {story.title}
        Current scene: {current_scene_count + 1} of {total_planned}
        Remaining scenes until ending: {remaining_scenes}
        
        Previous scenes:
        {scenes_summary}
        
        Characters:
        {character_info}
        
        Selected story path: {choice.get('title')} - {choice.get('description')}
        Choice type: {choice.get('type')}
        Preview: {choice.get('preview', '')}
        
        Generate the next scene following this story path.
        
        IMPORTANT: 
        - If only {remaining_scenes} scenes remain, start moving toward conclusion
        - If this is the second-to-last scene, set up for the finale
        - If this is the last scene, provide a satisfying ending
        
        Keep it consistent with the characters and previous events.
        Age group: {age_group}
        Genre: {genre}
        
        Return JSON with this structure:
        {{
            "scene_number": {current_scene_count + 1},
            "title": "Scene Title",
            "content": "Scene narrative text (2-3 paragraphs, age-appropriate)",
            "text": "Same as content",
            "image_prompt": "Detailed visual description for image generation including: {art_style} style, characters present, setting, mood, and action",
            "characters_present": ["Names of characters in this scene"]
        }}
        """
        
        try:
            scene_data = self.gemini.generate_json(
                prompt=prompt,
                system_prompt="Generate the next story scene dynamically based on reader choice"
            )
            
            # Add scene to story cache
            if scene_data:
                new_scene = Scene(
                    scene_number=scene_data.get('scene_number', current_scene_count + 1),
                    title=scene_data.get('title', ''),
                    text=scene_data.get('text', scene_data.get('content', '')),
                    image_prompt=scene_data.get('image_prompt', ''),
                    characters_present=scene_data.get('characters_present', [])
                )
                story.scenes.append(new_scene)
                self.cache.store_story(story)
                
                # Return scene data for frontend
                return {
                    "scene": new_scene.to_dict(),
                    "is_final": remaining_scenes == 1,
                    "scenes_remaining": remaining_scenes - 1
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate scene: {e}")
            return None