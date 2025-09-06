"""
Error handling utilities
"""

from functools import wraps
from flask import jsonify
import logging
import traceback

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API error"""
    def __init__(self, message, status_code=400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message, details=None):
        super().__init__(message, 400, details)

def handle_api_error(func):
    """Decorator for handling API errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.error(f"API Error in {func.__name__}: {e.message}")
            response = {"error": e.message}
            if e.details:
                response["details"] = e.details
            return jsonify(response), e.status_code
        except ValidationError as e:
            logger.error(f"Validation Error in {func.__name__}: {e.message}")
            response = {"error": e.message}
            if e.details:
                response["details"] = e.details
            return jsonify(response), 400
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": "An unexpected error occurred",
                "message": str(e)
            }), 500
    
    return wrapper

def log_request(func):
    """Decorator for logging API requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        logger.info(f"API Request: {request.method} {request.path}")
        if request.json:
            logger.debug(f"Request body: {request.json}")
        result = func(*args, **kwargs)
        logger.info(f"API Response: {request.method} {request.path} completed")
        return result
    
    return wrapper