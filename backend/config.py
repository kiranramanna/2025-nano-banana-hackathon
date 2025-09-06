"""
Configuration management module
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    
    # Server Configuration
    PORT = int(os.getenv('BACKEND_PORT', 5001))
    HOST = '0.0.0.0'
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Paths
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../public')
    IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
    STORY_FOLDER = os.path.join(UPLOAD_FOLDER, 'stories')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '../output')
    
    # Model Configuration
    TEXT_MODEL = os.getenv('TEXT_MODEL', 'gemini-1.5-flash')
    # Image-capable model via google-genai (as in notebook guide)
    IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'gemini-2.5-flash-image-preview')
    IMAGE_EDIT_MODEL = os.getenv('IMAGE_EDIT_MODEL', 'gemini-1.5-flash')
    
    # Generation Settings
    DEFAULT_TEMPERATURE = 0.9
    MAX_OUTPUT_TOKENS = 2000
    DEFAULT_NUM_SCENES = 5
    DEFAULT_AGE_GROUP = '7-10'
    DEFAULT_GENRE = 'adventure'
    DEFAULT_ART_STYLE = 'watercolor'
    
    # Image Settings
    DEFAULT_ASPECT_RATIO = '16:9'
    IMAGE_SAFETY_FILTER = 'block_few'
    ALLOW_PERSON_GENERATION = 'allow_all'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        
        # Create necessary directories
        for folder in [cls.UPLOAD_FOLDER, cls.IMAGE_FOLDER, 
                      cls.STORY_FOLDER, cls.OUTPUT_FOLDER]:
            os.makedirs(folder, exist_ok=True)
        
        return True

config = Config()
