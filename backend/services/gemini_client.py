"""
Gemini API client service (using google-genai for both text and images)
"""

import logging
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

from config import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Gemini API operations (text + image)"""

    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.text_model = config.TEXT_MODEL
        self.image_model = config.IMAGE_MODEL or 'gemini-2.5-flash-image-preview'

    def _extract_text(self, response: Any) -> str:
        # Prefer response.text if available; else join all text parts
        txt = getattr(response, 'text', None)
        if txt:
            return txt.strip()
        parts = []
        for part in getattr(response, 'parts', []) or []:
            t = getattr(part, 'text', None)
            if t:
                parts.append(t)
        return "\n".join(parts).strip()

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """Generate text using google-genai client"""
        try:
            full_prompt = (system_prompt + "\n\n" if system_prompt else "") + prompt
            cfg = types.GenerateContentConfig(
                temperature=temperature or config.DEFAULT_TEMPERATURE,
                max_output_tokens=max_tokens or config.MAX_OUTPUT_TOKENS,
                response_modalities=['Text'],
            )
            resp = self.client.models.generate_content(
                model=self.text_model,
                contents=full_prompt,
                config=cfg,
            )
            return self._extract_text(resp)
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            raise

    def generate_json(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        try:
            full_prompt = (system_prompt + "\n\n" if system_prompt else "") + prompt
            full_prompt += "\n\nReturn response as valid JSON only."
            text = self.generate_text(full_prompt)
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            import json
            return json.loads(text)
        except Exception as e:
            logger.error(f"JSON generation error: {e}")
            raise

    def generate_image(self, prompt: str, aspect_ratio: str = None) -> Any:
        """Generate an image using google-genai (returns PIL.Image)."""
        try:
            # Use generate_content with response_modalities as in the notebook
            resp = self.client.models.generate_content(
                model=self.image_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # Extract image from response parts (as in notebook code)
            genai_image = None
            for part in resp.parts:
                if hasattr(part, 'as_image'):
                    image = part.as_image()
                    if image:
                        genai_image = image
                        break
            
            if genai_image is None:
                raise RuntimeError('No image returned from model')
            
            # Convert google.genai.types.Image to PIL Image
            from PIL import Image as PILImage
            import io
            
            # Try to get the image data and convert to PIL
            if hasattr(genai_image, '_pil'):
                # If it has a _pil attribute, use it directly
                return genai_image._pil
            elif hasattr(genai_image, 'data'):
                # If it has raw data, convert it
                return PILImage.open(io.BytesIO(genai_image.data))
            else:
                # Return as is and let the caller handle it
                return genai_image
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            raise

    def edit_image(
        self, image_data: bytes, prompt: str, mime_type: str = "image/png"
    ) -> Any:
        """Edit an existing image using prompt + reference; returns PIL.Image or None."""
        try:
            import io
            import PIL.Image
            
            # Open the image as PIL.Image (matching notebook code)
            ref_image = PIL.Image.open(io.BytesIO(image_data))
            
            # Use generate_content with prompt and PIL image (exactly as in notebook)
            resp = self.client.models.generate_content(
                model=self.image_model,
                contents=[
                    prompt,
                    ref_image  # Pass PIL.Image directly
                ],
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # Extract image from response parts (same as generate_image)
            genai_image = None
            for part in resp.parts:
                if hasattr(part, 'as_image'):
                    image = part.as_image()
                    if image:
                        genai_image = image
                        break
            
            if genai_image is None:
                return None
            
            # Convert google.genai.types.Image to PIL Image or return as is
            import io
            if hasattr(genai_image, '_pil'):
                return genai_image._pil
            elif hasattr(genai_image, 'data'):
                return PILImage.open(io.BytesIO(genai_image.data))
            else:
                # Return the google.genai.types.Image directly
                # The caller can use its save() method
                return genai_image
        except Exception as e:
            logger.error(f"Image edit error: {e}")
            return None
