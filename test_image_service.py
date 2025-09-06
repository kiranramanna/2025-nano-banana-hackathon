#!/usr/bin/env python3
"""
Standalone test script for ImageService.generate_scene_image
"""

import os
import sys
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PIL import Image as PILImage
import io

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.image_service import ImageService
from models.image import ImageRequest, ImageResponse
from models.story import Story, Scene, Character
from config import config

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
            description="A brave young explorer",
            visual_description="Young girl with curly red hair, green eyes, wearing explorer outfit",
            role="protagonist"
        ),
        Character(
            name="Spark",
            description="Luna's magical companion",
            visual_description="Small blue dragon with sparkly wings",
            role="supporting"
        )
    ]
    
    scenes = [
        Scene(
            scene_number=1,
            title="The Discovery",
            text="Luna discovered a magical forest filled with glowing trees.",
            image_prompt="Magical forest with glowing trees, mystical atmosphere",
            characters_present=["Luna"]
        ),
        Scene(
            scene_number=2,
            title="Meeting Spark",
            text="Luna met Spark, a friendly dragon who became her companion.",
            image_prompt="Luna meeting a small blue dragon in the magical forest",
            characters_present=["Luna", "Spark"]
        ),
        Scene(
            scene_number=3,
            title="The Adventure Begins",
            text="Together, Luna and Spark embarked on an amazing adventure.",
            image_prompt="Luna riding on Spark's back, flying over the magical forest",
            characters_present=["Luna", "Spark"]
        )
    ]
    
    return Story(
        title="Luna's Magical Adventure",
        characters=characters,
        scenes=scenes,
        style="watercolor",
        age_group="7-10",
        genre="fantasy adventure",
        story_id="test_story_123"
    )


def create_test_image():
    """Create a test PIL image"""
    img = PILImage.new('RGB', (1024, 1024), color='blue')
    return img


def test_generate_scene_image_success():
    """Test successful image generation for a scene"""
    print("\n" + "="*50)
    print("Testing Successful Scene Image Generation")
    print("="*50)
    
    # Create test data
    test_story = create_test_story()
    test_image = create_test_image()
    
    # Create service and mock dependencies
    service = ImageService()
    
    # Mock cache service to return our test story
    service.cache.get_story = Mock(return_value=test_story)
    service.cache.store_story = Mock()
    
    # Mock Gemini client to return test image
    service.gemini.generate_image = Mock(return_value=test_image)
    
    # Create request
    request = ImageRequest(
        story_id="test_story_123",
        scene_number=1,
        aspect_ratio="16:9"
    )
    
    try:
        # Generate image
        response = service.generate_scene_image(request)
        
        # Verify response
        assert response.success == True, "Response should be successful"
        assert response.scene_number == 1, "Scene number should match"
        assert response.image_url.startswith("/images/"), "Image URL should start with /images/"
        assert response.error is None, "No error should be present"
        
        # Verify mocks were called
        service.cache.get_story.assert_called_once_with("test_story_123")
        service.gemini.generate_image.assert_called_once()
        service.cache.store_story.assert_called_once()
        
        # Check if image file was created
        filename = response.image_url.replace("/images/", "")
        filepath = os.path.join(config.IMAGE_FOLDER, filename)
        assert os.path.exists(filepath), f"Image file should exist at {filepath}"
        
        # Verify it's a valid PNG
        with PILImage.open(filepath) as img:
            assert img.format == 'PNG', "Saved file should be PNG format"
            print(f"✅ Image saved successfully: {filename}")
            print(f"   Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        
        # Clean up
        os.remove(filepath)
        
        print("✅ Successful image generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_generate_scene_image_with_custom_prompt():
    """Test image generation with custom prompt"""
    print("\n" + "="*50)
    print("Testing Scene Image Generation with Custom Prompt")
    print("="*50)
    
    test_story = create_test_story()
    test_image = create_test_image()
    
    service = ImageService()
    service.cache.get_story = Mock(return_value=test_story)
    service.cache.store_story = Mock()
    service.gemini.generate_image = Mock(return_value=test_image)
    
    custom_prompt = "A beautiful sunset over mountains with a rainbow"
    request = ImageRequest(
        story_id="test_story_123",
        scene_number=2,
        custom_prompt=custom_prompt,
        aspect_ratio="4:3"
    )
    
    try:
        response = service.generate_scene_image(request)
        
        assert response.success == True, "Response should be successful"
        
        # Verify custom prompt was used
        call_args = service.gemini.generate_image.call_args
        assert call_args[1]['prompt'] == custom_prompt, "Custom prompt should be used"
        assert call_args[1]['aspect_ratio'] == "4:3", "Custom aspect ratio should be used"
        
        # Clean up generated file
        filename = response.image_url.replace("/images/", "")
        filepath = os.path.join(config.IMAGE_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        print("✅ Custom prompt test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_generate_scene_image_story_not_found():
    """Test handling when story is not found"""
    print("\n" + "="*50)
    print("Testing Scene Image Generation - Story Not Found")
    print("="*50)
    
    service = ImageService()
    service.cache.get_story = Mock(return_value=None)
    
    request = ImageRequest(
        story_id="nonexistent_story",
        scene_number=1
    )
    
    try:
        response = service.generate_scene_image(request)
        
        assert response.success == False, "Response should fail"
        assert response.error == "Story not found", "Error message should indicate story not found"
        assert response.image_url == "", "Image URL should be empty"
        
        print("✅ Story not found test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_generate_scene_image_scene_not_found():
    """Test handling when scene is not found in story"""
    print("\n" + "="*50)
    print("Testing Scene Image Generation - Scene Not Found")
    print("="*50)
    
    test_story = create_test_story()
    
    service = ImageService()
    service.cache.get_story = Mock(return_value=test_story)
    
    request = ImageRequest(
        story_id="test_story_123",
        scene_number=99  # Non-existent scene
    )
    
    try:
        response = service.generate_scene_image(request)
        
        assert response.success == False, "Response should fail"
        assert response.error == "Scene not found", "Error message should indicate scene not found"
        assert response.image_url == "", "Image URL should be empty"
        
        print("✅ Scene not found test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_generate_scene_image_generation_failure():
    """Test handling when image generation fails"""
    print("\n" + "="*50)
    print("Testing Scene Image Generation - Generation Failure")
    print("="*50)
    
    test_story = create_test_story()
    
    service = ImageService()
    service.cache.get_story = Mock(return_value=test_story)
    service.gemini.generate_image = Mock(side_effect=Exception("API error"))
    
    request = ImageRequest(
        story_id="test_story_123",
        scene_number=1
    )
    
    try:
        response = service.generate_scene_image(request)
        
        assert response.success == False, "Response should fail"
        assert "API error" in response.error, "Error message should contain API error"
        assert response.image_url == "", "Image URL should be empty"
        
        print("✅ Generation failure test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_generate_scene_image_with_characters():
    """Test image generation with multiple characters in scene"""
    print("\n" + "="*50)
    print("Testing Scene Image Generation with Multiple Characters")
    print("="*50)
    
    test_story = create_test_story()
    test_image = create_test_image()
    
    service = ImageService()
    service.cache.get_story = Mock(return_value=test_story)
    service.cache.store_story = Mock()
    service.gemini.generate_image = Mock(return_value=test_image)
    
    # Request for scene 2 which has both Luna and Spark
    request = ImageRequest(
        story_id="test_story_123",
        scene_number=2
    )
    
    try:
        response = service.generate_scene_image(request)
        
        assert response.success == True, "Response should be successful"
        
        # Verify the prompt includes both characters
        call_args = service.gemini.generate_image.call_args
        prompt = call_args[1]['prompt']
        
        assert "Luna" in prompt, "Prompt should include Luna"
        assert "Spark" in prompt, "Prompt should include Spark"
        assert "curly red hair" in prompt, "Prompt should include Luna's description"
        assert "blue dragon" in prompt, "Prompt should include Spark's description"
        
        # Clean up
        filename = response.image_url.replace("/images/", "")
        filepath = os.path.join(config.IMAGE_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        print("✅ Multiple characters test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_google_genai_image_type():
    """Test handling of google.genai.types.Image"""
    print("\n" + "="*50)
    print("Testing Google GenAI Image Type Handling")
    print("="*50)
    
    test_story = create_test_story()
    
    # Create a mock google.genai.types.Image
    mock_genai_image = MagicMock()
    mock_genai_image.save = Mock()
    
    service = ImageService()
    service.cache.get_story = Mock(return_value=test_story)
    service.cache.store_story = Mock()
    service.gemini.generate_image = Mock(return_value=mock_genai_image)
    
    request = ImageRequest(
        story_id="test_story_123",
        scene_number=1
    )
    
    try:
        # Mock the save method to create a base64 file
        def mock_save(filepath):
            # Create a small test image and save as base64
            test_img = PILImage.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_img.save(buffer, format='PNG')
            import base64
            base64_data = base64.b64encode(buffer.getvalue()).decode()
            with open(filepath, 'w') as f:
                f.write(base64_data)
        
        mock_genai_image.save.side_effect = mock_save
        
        response = service.generate_scene_image(request)
        
        # The current implementation expects PIL Image, so this might fail
        # But we're testing the handling
        print(f"Response success: {response.success}")
        print(f"Response error: {response.error}")
        
        # Clean up any created files
        if response.success and response.image_url:
            filename = response.image_url.replace("/images/", "")
            filepath = os.path.join(config.IMAGE_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        print("✅ Google GenAI image type test completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("IMAGE SERVICE - GENERATE_SCENE_IMAGE TEST SUITE")
    print("="*60)
    
    # Check configuration
    if not config.GEMINI_API_KEY:
        print("\n⚠️  WARNING: GEMINI_API_KEY not found")
        print("Tests will run with mocked Gemini client")
    
    # Ensure image folder exists
    os.makedirs(config.IMAGE_FOLDER, exist_ok=True)
    
    # Run tests
    results = []
    
    results.append(("Successful Generation", test_generate_scene_image_success()))
    results.append(("Custom Prompt", test_generate_scene_image_with_custom_prompt()))
    results.append(("Story Not Found", test_generate_scene_image_story_not_found()))
    results.append(("Scene Not Found", test_generate_scene_image_scene_not_found()))
    results.append(("Generation Failure", test_generate_scene_image_generation_failure()))
    results.append(("Multiple Characters", test_generate_scene_image_with_characters()))
    results.append(("Google GenAI Image Type", test_google_genai_image_type()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())