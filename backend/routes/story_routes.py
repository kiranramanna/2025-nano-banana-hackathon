"""
Story-related API routes
"""

from flask import Blueprint, request, jsonify
from services import StoryService
from utils.validators import validate_story_request
from utils.error_handler import handle_api_error
import logging

logger = logging.getLogger(__name__)

story_bp = Blueprint('story', __name__)
story_service = StoryService()

@story_bp.route('/generate-story', methods=['POST'])
@handle_api_error
def generate_story():
    """Generate a new story from prompt"""
    data = request.json
    
    # Validate request
    errors = validate_story_request(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400
    
    # Extract parameters
    prompt = data.get('prompt')
    age_group = data.get('age_group', '7-10')
    genre = data.get('genre', 'adventure')
    num_scenes = data.get('num_scenes', 5)
    art_style = data.get('art_style', 'watercolor')
    
    # Generate story
    story = story_service.generate_story(
        prompt=prompt,
        age_group=age_group,
        genre=genre,
        num_scenes=num_scenes,
        art_style=art_style
    )
    
    return jsonify({
        "story_id": story.story_id,
        "story": story.to_dict()
    })

@story_bp.route('/get-story/<story_id>', methods=['GET'])
@handle_api_error
def get_story(story_id):
    """Get story by ID"""
    story = story_service.get_story(story_id)
    
    if not story:
        return jsonify({"error": "Story not found"}), 404
    
    return jsonify(story.to_dict())

@story_bp.route('/stories', methods=['GET'])
@handle_api_error
def list_stories():
    """List all available stories"""
    stories = story_service.list_stories()
    return jsonify(stories)

@story_bp.route('/update-character', methods=['PUT'])
@handle_api_error
def update_character():
    """Update character details"""
    data = request.json
    
    story_id = data.get('story_id')
    character_name = data.get('character_name')
    updates = data.get('updates', {})
    
    if not all([story_id, character_name]):
        return jsonify({"error": "story_id and character_name are required"}), 400
    
    success = story_service.update_character(story_id, character_name, updates)
    
    if success:
        return jsonify({"success": True, "message": "Character updated"})
    else:
        return jsonify({"error": "Failed to update character"}), 400

@story_bp.route('/delete-story/<story_id>', methods=['DELETE'])
@handle_api_error
def delete_story(story_id):
    """Delete a story"""
    from services import CacheService
    cache = CacheService()
    
    success = cache.delete_story(story_id)
    
    if success:
        return jsonify({"success": True, "message": "Story deleted"})
    else:
        return jsonify({"error": "Story not found"}), 404

@story_bp.route('/story-choices', methods=['POST'])
@handle_api_error
def get_story_choices():
    """Generate story branching choices for the next scene"""
    data = request.json
    
    current_scene = data.get('currentScene')
    story_context = data.get('storyContext', {})
    
    if not current_scene:
        return jsonify({"error": "Current scene is required"}), 400
    
    # Generate 4 different story choices
    choices = story_service.generate_story_choices(
        current_scene=current_scene,
        genre=story_context.get('genre', 'adventure'),
        age_group=story_context.get('ageGroup', '7-10')
    )
    
    return jsonify({"choices": choices})

@story_bp.route('/generate-scene-from-choice', methods=['POST'])
@handle_api_error
def generate_scene_from_choice():
    """Generate a new scene based on selected story choice"""
    data = request.json
    
    story_id = data.get('storyId')
    choice = data.get('choice')
    story_context = data.get('storyContext', {})
    
    if not all([story_id, choice]):
        return jsonify({"error": "story_id and choice are required"}), 400
    
    # Generate new scene based on choice
    scene = story_service.generate_scene_from_choice(
        story_id=story_id,
        choice=choice,
        genre=story_context.get('genre', 'adventure'),
        age_group=story_context.get('ageGroup', '7-10'),
        art_style=story_context.get('artStyle', 'watercolor')
    )
    
    if scene:
        return jsonify({"scene": scene})
    else:
        return jsonify({"error": "Failed to generate scene"}), 500