"""
Export API routes
"""

from flask import Blueprint, request, jsonify, send_from_directory
from services import ExportService, CacheService
from models.export import ExportRequest
from utils.error_handler import handle_api_error
from config import config
import os
import logging

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__)
export_service = ExportService()
cache_service = CacheService()

@export_bp.route('/pdf', methods=['POST'])
@handle_api_error
def export_pdf():
    """Export story as PDF"""
    data = request.json
    
    story_id = data.get('story_id')
    if not story_id:
        return jsonify({"error": "story_id is required"}), 400
    
    story = cache_service.get_story(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404
    
    export_request = ExportRequest(
        story_id=story_id,
        format='pdf',
        images=data.get('images', {}),
        filename=data.get('filename'),
        include_images=data.get('include_images', True),
        include_metadata=data.get('include_metadata', True)
    )
    
    filename = export_service.export_story(story, export_request)
    
    if filename:
        return jsonify({
            "success": True,
            "file": f"/output/{filename}",
            "filename": filename
        })
    else:
        return jsonify({"error": "Failed to export PDF"}), 500

@export_bp.route('/html', methods=['POST'])
@handle_api_error
def export_html():
    """Export story as HTML"""
    data = request.json
    
    story_id = data.get('story_id')
    if not story_id:
        return jsonify({"error": "story_id is required"}), 400
    
    story = cache_service.get_story(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404
    
    export_request = ExportRequest(
        story_id=story_id,
        format='html',
        images=data.get('images', {}),
        filename=data.get('filename'),
        include_images=data.get('include_images', True),
        include_metadata=data.get('include_metadata', True)
    )
    
    filename = export_service.export_story(story, export_request)
    
    if filename:
        return jsonify({
            "success": True,
            "file": f"/output/{filename}",
            "filename": filename
        })
    else:
        return jsonify({"error": "Failed to export HTML"}), 500

@export_bp.route('/json', methods=['POST'])
@handle_api_error
def export_json():
    """Export story as JSON"""
    data = request.json
    
    story_id = data.get('story_id')
    if not story_id:
        return jsonify({"error": "story_id is required"}), 400
    
    story = cache_service.get_story(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404
    
    export_request = ExportRequest(
        story_id=story_id,
        format='json',
        images=data.get('images', {}),
        filename=data.get('filename'),
        include_images=data.get('include_images', True),
        include_metadata=data.get('include_metadata', True)
    )
    
    filename = export_service.export_story(story, export_request)
    
    if filename:
        return jsonify({
            "success": True,
            "file": f"/output/{filename}",
            "filename": filename
        })
    else:
        return jsonify({"error": "Failed to export JSON"}), 500

@export_bp.route('/download/<filename>', methods=['GET'])
@handle_api_error
def download_export(filename):
    """Download exported file"""
    return send_from_directory(
        config.OUTPUT_FOLDER,
        filename,
        as_attachment=True
    )

@export_bp.route('/list', methods=['GET'])
@handle_api_error
def list_exports():
    """List all exported files"""
    exports = []
    
    if os.path.exists(config.OUTPUT_FOLDER):
        for filename in os.listdir(config.OUTPUT_FOLDER):
            if not filename.startswith('temp_'):
                filepath = os.path.join(config.OUTPUT_FOLDER, filename)
                stats = os.stat(filepath)
                exports.append({
                    'filename': filename,
                    'size': stats.st_size,
                    'created': stats.st_ctime,
                    'type': os.path.splitext(filename)[1][1:]
                })
    
    # Sort by creation time (newest first)
    exports.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify(exports)