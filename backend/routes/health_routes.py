"""
Health check and system status routes
"""

from flask import Blueprint, jsonify
from config import config
import os
import psutil
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        "status": "healthy",
        "service": "AI Storybook Generator",
        "version": "1.0.0"
    })

@health_bp.route('/status', methods=['GET'])
def system_status():
    """Detailed system status"""
    try:
        # Check directory existence
        dirs_status = {
            'images': os.path.exists(config.IMAGE_FOLDER),
            'stories': os.path.exists(config.STORY_FOLDER),
            'output': os.path.exists(config.OUTPUT_FOLDER)
        }
        
        # Count files
        file_counts = {}
        for name, path in [
            ('images', config.IMAGE_FOLDER),
            ('stories', config.STORY_FOLDER),
            ('exports', config.OUTPUT_FOLDER)
        ]:
            try:
                if os.path.exists(path):
                    file_counts[name] = len(os.listdir(path))
                else:
                    file_counts[name] = 0
            except:
                file_counts[name] = 0
        
        # System resources
        memory = psutil.virtual_memory()
        
        return jsonify({
            "status": "operational",
            "api_key_configured": bool(config.GEMINI_API_KEY),
            "directories": dirs_status,
            "file_counts": file_counts,
            "system": {
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024)
            }
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@health_bp.route('/config', methods=['GET'])
def get_config():
    """Get public configuration (no sensitive data)"""
    return jsonify({
        "text_model": config.TEXT_MODEL,
        "image_model": config.IMAGE_MODEL,
        "default_temperature": config.DEFAULT_TEMPERATURE,
        "default_num_scenes": config.DEFAULT_NUM_SCENES,
        "default_age_group": config.DEFAULT_AGE_GROUP,
        "default_genre": config.DEFAULT_GENRE,
        "default_art_style": config.DEFAULT_ART_STYLE,
        "default_aspect_ratio": config.DEFAULT_ASPECT_RATIO
    })