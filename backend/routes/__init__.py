"""
API Routes
"""

from flask import Blueprint

# Import blueprints
from .story_routes import story_bp
from .image_routes import image_bp
from .export_routes import export_bp
from .health_routes import health_bp

# Export all blueprints
__all__ = [
    'story_bp',
    'image_bp',
    'export_bp',
    'health_bp'
]

def register_routes(app):
    """Register all route blueprints with the app"""
    app.register_blueprint(story_bp, url_prefix='/api')
    app.register_blueprint(image_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api/export')
    app.register_blueprint(health_bp, url_prefix='/api')