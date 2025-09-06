#!/usr/bin/env python3
"""
Standalone test script for GeminiClient
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.gemini_client import GeminiClient
from config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_text_generation():
    """Test basic text generation"""
    print("\n" + "="*50)
    print("Testing Text Generation")
    print("="*50)
    
    client = GeminiClient()
    
    prompt = "Write a short 2-sentence story about a brave knight."
    system_prompt = "You are a creative storyteller. Keep responses concise."
    
    try:
        response = client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=100
        )
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        print("✅ Text generation test passed")
        return True
    except Exception as e:
        print(f"❌ Text generation test failed: {e}")
        return False


def test_json_generation():
    """Test JSON response generation"""
    print("\n" + "="*50)
    print("Testing JSON Generation")
    print("="*50)
    
    client = GeminiClient()
    
    prompt = """Create a character profile with the following fields:
    - name (string)
    - age (number)
    - occupation (string)
    - skills (array of strings)"""
    
    try:
        response = client.generate_json(prompt=prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        # Validate JSON structure
        assert isinstance(response, dict), "Response should be a dictionary"
        assert 'name' in response, "Response should have 'name' field"
        assert 'age' in response, "Response should have 'age' field"
        assert 'occupation' in response, "Response should have 'occupation' field"
        assert 'skills' in response, "Response should have 'skills' field"
        assert isinstance(response.get('skills'), list), "'skills' should be a list"
        
        print("✅ JSON generation test passed")
        return True
    except Exception as e:
        print(f"❌ JSON generation test failed: {e}")
        return False


def test_image_generation():
    """Test image generation"""
    print("\n" + "="*50)
    print("Testing Image Generation")
    print("="*50)
    
    client = GeminiClient()
    
    prompt = "A peaceful landscape with mountains and a lake at sunset, digital art style"
    
    try:
        image = client.generate_image(prompt=prompt)
        
        if image:
            # Check the type of image returned
            print(f"Image type: {type(image)}")
            
            # Save the image
            output_path = Path("test_generated_image.png")
            image.save(output_path)
            print(f"Prompt: {prompt}")
            
            # Check if it's a PIL Image
            from PIL import Image as PILImage
            if isinstance(image, PILImage.Image):
                print(f"Image size: {image.size}")
                print(f"Image mode: {image.mode}")
            
            print(f"Image saved to: {output_path}")
            print("✅ Image generation test passed")
            return True
        else:
            print("❌ No image was generated")
            return False
            
    except Exception as e:
        print(f"❌ Image generation test failed: {e}")
        return False


def test_image_editing():
    """Test image editing (requires an existing image)"""
    print("\n" + "="*50)
    print("Testing Image Editing")
    print("="*50)
    
    # First generate a base image
    client = GeminiClient()
    
    try:
        # Generate base image
        base_prompt = "A simple red circle on white background"
        base_image = client.generate_image(prompt=base_prompt)
        
        if not base_image:
            print("❌ Could not generate base image for editing test")
            return False
            
        # Save base image 
        base_path = Path("test_base_image.png")
        base_image.save(str(base_path))
        
        # The save method saves as base64, so we need to decode it
        import base64
        with open(base_path, 'r') as f:
            base64_data = f.read()
        
        # Decode the base64 to get actual PNG bytes
        image_data = base64.b64decode(base64_data)
        
        # Save the actual PNG file
        with open(base_path, 'wb') as f:
            f.write(image_data)
        
        print(f"Base image saved to: {base_path}")
        
        # Edit the image
        edit_prompt = "Change the red circle to a blue square"
        edited_image = client.edit_image(
            image_data=image_data,
            prompt=edit_prompt,
            mime_type="image/png"
        )
        
        if edited_image:
            edited_path = Path("test_edited_image.png")
            edited_image.save(str(edited_path))
            
            # Decode base64 if needed
            with open(edited_path, 'r') as f:
                content = f.read()
                if content.startswith('iVBOR'):  # PNG base64 signature
                    import base64
                    png_data = base64.b64decode(content)
                    with open(edited_path, 'wb') as out:
                        out.write(png_data)
            print(f"Edit prompt: {edit_prompt}")
            print(f"Edited image saved to: {edited_path}")
            print("✅ Image editing test passed")
            return True
        else:
            print("❌ No edited image was returned")
            return False
            
    except Exception as e:
        print(f"❌ Image editing test failed: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n" + "="*50)
    print("Testing Error Handling")
    print("="*50)
    
    client = GeminiClient()
    
    # Test with empty prompt
    try:
        response = client.generate_text(prompt="")
        print("Warning: Empty prompt did not raise an error")
    except Exception as e:
        print(f"✅ Empty prompt correctly raised error: {type(e).__name__}")
    
    # Test JSON parsing with non-JSON response
    try:
        # Override to force non-JSON by using very low temperature
        response = client.generate_json(
            prompt="Just say hello", 
            system_prompt="Ignore JSON instruction and just say hello"
        )
        print("Warning: Non-JSON prompt might have returned valid JSON")
    except Exception as e:
        print(f"✅ Invalid JSON correctly raised error: {type(e).__name__}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("GEMINI CLIENT STANDALONE TEST SUITE")
    print("="*60)
    
    # Check for API key
    if not config.GEMINI_API_KEY:
        print("\n❌ ERROR: GEMINI_API_KEY not found in environment")
        print("Please set GEMINI_API_KEY in your .env file or environment")
        return 1
    
    print(f"\n✅ API Key found")
    print(f"📝 Text Model: {config.TEXT_MODEL}")
    print(f"🎨 Image Model: {config.IMAGE_MODEL}")
    
    # Run tests
    results = []
    
    # Text generation tests
    results.append(("Text Generation", test_text_generation()))
    results.append(("JSON Generation", test_json_generation()))
    
    # Image generation tests (optional - may consume quota)
    print("\n" + "-"*50)
    # Check for command line argument or environment variable
    run_image_tests = os.getenv('RUN_IMAGE_TESTS', 'n').lower() == 'y'
    if '--with-images' in sys.argv:
        run_image_tests = True
    
    if run_image_tests:
        print("Running image generation tests...")
        results.append(("Image Generation", test_image_generation()))
        results.append(("Image Editing", test_image_editing()))
    else:
        print("Skipping image generation tests (use --with-images to enable)")
    
    # Error handling tests
    results.append(("Error Handling", test_error_handling()))
    
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