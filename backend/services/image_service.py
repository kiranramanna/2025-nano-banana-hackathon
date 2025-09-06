"""
Image generation and management service
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from PIL import Image as PILImage
from models.image import ImageRequest, ImageResponse
from models.story import Story
from .gemini_client import GeminiClient
from .cache_service import CacheService
from config import config

logger = logging.getLogger(__name__)

class ImageService:
    """Service for image generation and management"""
    
    def __init__(self):
        self.gemini = GeminiClient()
        self.cache = CacheService()
    
    def generate_scene_image(self, request: ImageRequest) -> ImageResponse:
        """Generate image for a story scene"""
        
        story = self.cache.get_story(request.story_id)
        if not story:
            return ImageResponse(
                image_url='',
                scene_number=request.scene_number,
                success=False,
                error='Story not found'
            )
        
        scene = self._get_scene(story, request.scene_number)
        if not scene:
            return ImageResponse(
                image_url='',
                scene_number=request.scene_number,
                success=False,
                error='Scene not found'
            )
        
        try:
            # Build image prompt
            prompt = self._build_image_prompt(
                story, scene, request.custom_prompt
            )
            
            # Generate image
            image = self.gemini.generate_image(
                prompt=prompt,
                aspect_ratio=request.aspect_ratio
            )
            
            if not image:
                raise Exception("Failed to generate image")
            
            # Save image
            filename = self._save_image(
                image, request.story_id, request.scene_number
            )
            
            image_url = f"/images/{filename}"
            
            # Update scene with image URL
            scene.image_url = image_url
            self.cache.store_story(story)
            
            return ImageResponse(
                image_url=image_url,
                scene_number=request.scene_number,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return ImageResponse(
                image_url='',
                scene_number=request.scene_number,
                success=False,
                error=str(e)
            )
    
    def refine_character_image(self,
                              story_id: str,
                              character_name: str,
                              reference_image_path: str) -> bool:
        """Refine character based on reference image"""
        
        story = self.cache.get_story(story_id)
        if not story:
            return False
        
        character = self._get_character(story, character_name)
        if not character:
            return False
        
        try:
            # Read reference image
            with open(reference_image_path, 'rb') as f:
                image_data = f.read()
            
            # Build refinement prompt
            prompt = f"""
            Analyze this character and remember their exact appearance:
            Character: {character.name}
            Description: {character.visual_description}
            
            Extract and remember:
            - Exact facial features
            - Hair color and style
            - Clothing details
            - Distinctive marks
            - Body proportions
            
            This will be used to maintain consistency across all scenes.
            """
            
            # Process with Gemini
            response = self.gemini.generate_text(prompt)
            
            # Update character with refined description
            character.refined_description = response
            self.cache.store_story(story)
            
            return True
            
        except Exception as e:
            logger.error(f"Character refinement failed: {e}")
            return False
    
    def _build_image_prompt(self,
                           story: Story,
                           scene: any,
                           custom_prompt: Optional[str] = None) -> str:
        """Build prompt for image generation"""
        
        if custom_prompt:
            return custom_prompt
        
        # Get characters in scene
        characters_descriptions = []
        for char_name in scene.characters_present:
            char = self._get_character(story, char_name)
            if char:
                desc = char.refined_description or char.visual_description
                characters_descriptions.append(f"{char.name}: {desc}")
        
        prompt = f"""
        Art Style: {story.style}
        
        Scene Description: {scene.image_prompt}
        
        Characters in Scene:
        {chr(10).join(characters_descriptions)}
        
        IMPORTANT REQUIREMENTS:
        1. Maintain EXACT character appearances as described
        2. Keep the art style consistent as {story.style}
        3. Age-appropriate for {story.age_group} year olds
        4. Bright, engaging colors
        5. Clear character expressions and actions
        6. No text or words in the image
        """
        
        return prompt
    
    def _save_image(self, image: any, story_id: str, scene_number: int) -> str:
        """Save generated image to disk as a valid PNG with safe conversion."""
        from PIL import Image as PILImage
        import base64
        os.makedirs(config.IMAGE_FOLDER, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scene_{story_id}_{scene_number}_{timestamp}.png"
        filepath = os.path.join(config.IMAGE_FOLDER, filename)

        try:
            # Check if it's a google.genai.types.Image
            if hasattr(image, 'save') and not isinstance(image, PILImage.Image):
                # It's a google.genai.types.Image, use its save method
                image.save(filepath)
                
                # The save method saves as base64, so decode it
                with open(filepath, 'r') as f:
                    base64_data = f.read()
                
                # Decode base64 to get actual PNG bytes
                png_data = base64.b64decode(base64_data)
                
                # Save the actual PNG file
                with open(filepath, 'wb') as f:
                    f.write(png_data)
                    
            elif isinstance(image, PILImage.Image):
                # It's already a PIL Image
                # Convert to a compatible mode for PNG
                if image.mode not in ("RGB", "RGBA", "L", "LA"):
                    image = image.convert("RGB")
                
                # Save explicitly as PNG
                image.save(filepath, format="PNG", optimize=True)
            else:
                # Try other conversion methods
                pil = None
                
                # Try Google part.as_image() accessor if present
                try:
                    as_image = getattr(image, 'as_image', None)
                    if callable(as_image):
                        pil = as_image()
                except Exception:
                    pass
                    
                if not pil:
                    # Try to coerce if possible (e.g., binary-like object)
                    try:
                        from io import BytesIO
                        data = None
                        # Common attributes on display/binary objects
                        for attr in ("data", "bytes", "value", "buffer"):
                            if hasattr(image, attr):
                                data = getattr(image, attr)
                                break
                        if data is not None:
                            pil = PILImage.open(BytesIO(data))
                    except Exception:
                        pass
                
                if pil and isinstance(pil, PILImage.Image):
                    # Convert to a compatible mode for PNG
                    if pil.mode not in ("RGB", "RGBA", "L", "LA"):
                        pil = pil.convert("RGB")
                    pil.save(filepath, format="PNG", optimize=True)
                else:
                    raise TypeError("Could not convert image to PIL Image")

            # Optional basic verification: try open and load
            try:
                with PILImage.open(filepath) as check:
                    check.load()
            except Exception as e:
                logger.warning(f"Saved image verification failed: {e}")

            logger.info(f"Image saved: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    def _get_scene(self, story: Story, scene_number: int):
        """Get scene by number"""
        for scene in story.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None
    
    def _get_character(self, story: Story, character_name: str):
        """Get character by name"""
        for char in story.characters:
            if char.name == character_name:
                return char
        return None
