#!/usr/bin/env python3
"""
AI Storybook Generator - Modular Backend Application
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from config import config
from routes import register_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register all route blueprints
    register_routes(app)
    
    # Static file routes for generated content
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve generated images"""
        return send_from_directory(config.IMAGE_FOLDER, filename)
    
    @app.route('/output/<path:filename>')
    def serve_export(filename):
        """Serve exported files"""
        return send_from_directory(config.OUTPUT_FOLDER, filename, as_attachment=True)
    
    # Serve frontend files
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    # Serve CSS files
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(frontend_dir, 'css'), filename)
    
    # Serve JS files
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(frontend_dir, 'js'), filename)

    # Serve HTML component files
    @app.route('/html/<path:filename>')
    def serve_html(filename):
        """Serve HTML component fragments for the frontend"""
        return send_from_directory(os.path.join(frontend_dir, 'html'), filename)

    # Serve the main styles.css
    @app.route('/styles.css')
    def serve_styles():
        return send_from_directory(frontend_dir, 'styles.css')
    
    # Serve index.html at root
    @app.route('/')
    def index():
        """Serve the frontend application"""
        index_path = os.path.join(frontend_dir, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            # Fallback to API info if frontend not found
            return {
                "service": "AI Storybook Generator API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/api/health",
                    "status": "/api/status",
                    "generate_story": "/api/generate-story",
                    "list_stories": "/api/stories",
                    "generate_image": "/api/generate-scene-image",
                    "export": "/api/export/{format}"
                }
            }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return {"error": "Internal server error"}, 500
    
    return app

def main():
    """Main entry point"""
    app = create_app()
    
    logger.info(f"Starting AI Storybook Generator on {config.HOST}:{config.PORT}")
    logger.info(f"Debug mode: {config.DEBUG}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

if __name__ == '__main__':
    main()
