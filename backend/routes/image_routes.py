"""
Image generation API routes
"""

from flask import Blueprint, request, jsonify
from services import ImageService, CacheService
from models.image import ImageRequest
from utils.validators import validate_image_request
from utils.error_handler import handle_api_error
import logging

logger = logging.getLogger(__name__)

image_bp = Blueprint('image', __name__)
image_service = ImageService()

@image_bp.route('/generate-scene-image', methods=['POST'])
@handle_api_error
def generate_scene_image():
    """Generate image for a scene"""
    data = request.json
    
    # Validate request
    errors = validate_image_request(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400
    
    # Create image request
    image_request = ImageRequest(
        story_id=data.get('story_id'),
        scene_number=data.get('scene_number'),
        custom_prompt=data.get('custom_prompt'),
        style=data.get('style', 'watercolor'),
        aspect_ratio=data.get('aspect_ratio', '16:9'),
        regenerate=data.get('regenerate', False)
    )
    
    # Generate image
    response = image_service.generate_scene_image(image_request)
    
    if not response.success:
        return jsonify({"error": response.error}), 400
    
    return jsonify(response.to_dict())

@image_bp.route('/refine-character', methods=['POST'])
@handle_api_error
def refine_character():
    """Refine character appearance from reference image"""
    data = request.json
    
    story_id = data.get('story_id')
    character_name = data.get('character_name')
    image_path = data.get('image_path')
    
    if not all([story_id, character_name, image_path]):
        return jsonify({
            "error": "story_id, character_name, and image_path are required"
        }), 400
    
    # Process image path
    if image_path.startswith('/images/'):
        import os
        from config import config
        image_path = os.path.join(config.IMAGE_FOLDER, 
                                 image_path.replace('/images/', ''))
    
    success = image_service.refine_character_image(
        story_id, character_name, image_path
    )
    
    if success:
        return jsonify({
            "success": True,
            "message": "Character refined successfully"
        })
    else:
        return jsonify({"error": "Failed to refine character"}), 400

@image_bp.route('/regenerate-all-images/<story_id>', methods=['POST'])
@handle_api_error
def regenerate_all_images(story_id):
    """Regenerate all images for a story"""
    cache = CacheService()
    story = cache.get_story(story_id)
    
    if not story:
        return jsonify({"error": "Story not found"}), 404
    
    results = []
    for scene in story.scenes:
        request = ImageRequest(
            story_id=story_id,
            scene_number=scene.scene_number,
            regenerate=True
        )
        response = image_service.generate_scene_image(request)
        results.append({
            "scene": scene.scene_number,
            "success": response.success,
            "image_url": response.image_url if response.success else None
        })
    
    return jsonify({
        "success": True,
        "results": results
    })