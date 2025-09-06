#!/usr/bin/env python3
"""
Real integration test for ImageService.generate_scene_image
This test actually calls the Gemini API and generates real images
"""

import os
import sys
import logging
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.image_service import ImageService
from services.cache_service import CacheService
from models.image import ImageRequest, ImageResponse
from models.story import Story, Scene, Character
from config import config
from PIL import Image as PILImage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_story():
    """Create a test story with characters and scenes"""
    characters = [
        Character(
            name="Luna",
            description="A brave young explorer with a curious mind",
            visual_description="Young girl with curly red hair, bright green eyes, freckles, wearing a purple explorer vest with many pockets, brown boots, and a small backpack",
            role="protagonist"
        ),
        Character(
            name="Spark",
            description="A playful magical dragon companion",
            visual_description="Small friendly blue dragon, about the size of a cat, with iridescent scales, purple wing membranes, golden eyes, and a glowing tail tip",
            role="supporting"
        )
    ]
    
    scenes = [
        Scene(
            scene_number=1,
            title="The Magical Discovery",
            text="Luna wandered into a forest she had never seen before. The trees sparkled with golden light, and mysterious flowers glowed in rainbow colors.",
            image_prompt="A young girl with red curly hair exploring a magical forest with glowing golden trees and rainbow-colored flowers, mystical atmosphere, soft magical lighting",
            characters_present=["Luna"]
        ),
        Scene(
            scene_number=2,
            title="Meeting a New Friend",
            text="From behind a glowing tree, a small blue dragon appeared. 'Hello!' said the dragon, 'My name is Spark!'",
            image_prompt="Young girl with red hair meeting a small friendly blue dragon in a magical forest, the dragon is emerging from behind a glowing tree, both looking happy and curious",
            characters_present=["Luna", "Spark"]
        ),
        Scene(
            scene_number=3,
            title="Flying Adventure",
            text="Luna climbed onto Spark's back, and together they soared above the magical forest, seeing wonders beyond imagination.",
            image_prompt="Girl with red hair riding on a small blue dragon's back, flying above a magical forest with golden trees below, clouds around them, sunset sky, adventure scene",
            characters_present=["Luna", "Spark"]
        )
    ]
    
    return Story(
        title="Luna's Magical Forest Adventure",
        characters=characters,
        scenes=scenes,
        style="watercolor illustration",
        age_group="7-10",
        genre="fantasy adventure",
        story_id="test_story_real_001"
    )


def test_generate_scene_image_real():
    """Test real image generation for scenes"""
    print("\n" + "="*60)
    print("REAL IMAGE GENERATION TEST")
    print("="*60)
    
    # Check for API key
    if not config.GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not found in environment")
        print("Please set GEMINI_API_KEY in your .env file")
        return False
    
    print(f"✅ API Key found")
    print(f"📝 Text Model: {config.TEXT_MODEL}")
    print(f"🎨 Image Model: {config.IMAGE_MODEL}")
    
    # Create test story
    test_story = create_test_story()
    print(f"\n📖 Test Story: {test_story.title}")
    print(f"   Characters: {', '.join([c.name for c in test_story.characters])}")
    print(f"   Scenes: {len(test_story.scenes)}")
    
    # Initialize services
    service = ImageService()
    cache = CacheService()
    
    # Store the test story in cache
    cache.store_story(test_story)
    print(f"✅ Story stored in cache with ID: {test_story.story_id}")
    
    # Test generating images for each scene
    results = []
    
    for scene_num in [1, 2, 3]:
        print(f"\n" + "-"*50)
        print(f"Testing Scene {scene_num}")
        print("-"*50)
        
        scene = test_story.scenes[scene_num - 1]
        print(f"Scene Title: {scene.title}")
        print(f"Characters: {', '.join(scene.characters_present)}")
        
        # Create request
        request = ImageRequest(
            story_id=test_story.story_id,
            scene_number=scene_num,
            aspect_ratio="16:9"
        )
        
        try:
            print("🎨 Generating image...")
            
            # Generate image (REAL API CALL)
            response = service.generate_scene_image(request)
            
            if response.success:
                print(f"✅ Image generated successfully!")
                print(f"   URL: {response.image_url}")
                
                # Verify the image file
                filename = response.image_url.replace("/images/", "")
                filepath = os.path.join(config.IMAGE_FOLDER, filename)
                
                if os.path.exists(filepath):
                    # Open and check the image
                    with PILImage.open(filepath) as img:
                        print(f"   Format: {img.format}")
                        print(f"   Size: {img.size}")
                        print(f"   Mode: {img.mode}")
                        
                        # Verify it's a valid PNG
                        assert img.format == 'PNG', "Image should be PNG format"
                        assert img.size[0] > 0 and img.size[1] > 0, "Image should have valid dimensions"
                        
                    # Get file size
                    file_size = os.path.getsize(filepath) / 1024  # KB
                    print(f"   File size: {file_size:.1f} KB")
                    
                    results.append((scene_num, True, filepath))
                else:
                    print(f"❌ Image file not found at {filepath}")
                    results.append((scene_num, False, None))
                    
            else:
                print(f"❌ Image generation failed: {response.error}")
                results.append((scene_num, False, None))
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            results.append((scene_num, False, None))
    
    # Test with custom prompt
    print(f"\n" + "-"*50)
    print("Testing with Custom Prompt")
    print("-"*50)
    
    custom_request = ImageRequest(
        story_id=test_story.story_id,
        scene_number=1,
        custom_prompt="A magical castle floating in the clouds at sunset, painted in watercolor style with soft pastel colors",
        aspect_ratio="4:3"
    )
    
    try:
        print("🎨 Generating image with custom prompt...")
        response = service.generate_scene_image(custom_request)
        
        if response.success:
            print(f"✅ Custom image generated successfully!")
            print(f"   URL: {response.image_url}")
            
            filename = response.image_url.replace("/images/", "")
            filepath = os.path.join(config.IMAGE_FOLDER, filename)
            
            if os.path.exists(filepath):
                with PILImage.open(filepath) as img:
                    print(f"   Format: {img.format}, Size: {img.size}")
                results.append(("Custom", True, filepath))
            else:
                results.append(("Custom", False, None))
        else:
            print(f"❌ Custom image generation failed: {response.error}")
            results.append(("Custom", False, None))
            
    except Exception as e:
        print(f"❌ Error with custom prompt: {e}")
        results.append(("Custom", False, None))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for scene_id, success, filepath in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        scene_label = f"Scene {scene_id}" if isinstance(scene_id, int) else scene_id
        print(f"{scene_label}: {status}")
        if success and filepath:
            print(f"   File: {os.path.basename(filepath)}")
    
    print(f"\nTotal: {successful}/{total} images generated successfully")
    
    # Cleanup question
    if successful > 0:
        print("\n" + "-"*50)
        print("Generated images are saved in:", config.IMAGE_FOLDER)
        print("You can view them to verify quality.")
        
        cleanup = input("\nDelete test images? (y/n): ").lower()
        if cleanup == 'y':
            for _, success, filepath in results:
                if success and filepath and os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Deleted: {os.path.basename(filepath)}")
            print("✅ Test images cleaned up")
        else:
            print("Images kept for review")
    
    return successful == total


def main():
    """Run the real integration test"""
    print("\n" + "="*70)
    print("IMAGE SERVICE - REAL INTEGRATION TEST")
    print("This test will make actual API calls to Gemini")
    print("="*70)
    
    # Ensure required directories exist
    os.makedirs(config.IMAGE_FOLDER, exist_ok=True)
    os.makedirs(config.STORY_FOLDER, exist_ok=True)
    
    # Run test
    success = test_generate_scene_image_real()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())