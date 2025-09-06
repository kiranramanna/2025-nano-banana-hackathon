"""
Export service for PDF, HTML, and other formats
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Optional
from io import BytesIO
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from models.story import Story
from models.export import ExportRequest
from config import config

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting stories in various formats"""
    
    def export_story(self, 
                    story: Story,
                    request: ExportRequest) -> Optional[str]:
        """Export story in requested format"""
        
        if request.format == 'pdf':
            return self._export_pdf(story, request)
        elif request.format == 'html':
            return self._export_html(story, request)
        elif request.format == 'json':
            return self._export_json(story, request)
        else:
            logger.error(f"Unsupported export format: {request.format}")
            return None
    
    def _export_pdf(self, story: Story, request: ExportRequest) -> Optional[str]:
        """Export story as PDF"""
        try:
            filename = request.filename or f"story_{story.story_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(config.OUTPUT_FOLDER, filename)
            
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            story_elements = []
            styles = self._get_pdf_styles()
            
            # Title page
            story_elements.append(
                Paragraph(story.title, styles['title'])
            )
            story_elements.append(Spacer(1, 0.5 * inch))
            
            # Metadata
            meta_text = f"Genre: {story.genre} | Age Group: {story.age_group}"
            story_elements.append(
                Paragraph(meta_text, styles['meta'])
            )
            story_elements.append(Spacer(1, 0.3 * inch))
            
            # Characters section
            if story.characters:
                story_elements.append(
                    Paragraph("Characters", styles['heading'])
                )
                for char in story.characters:
                    char_text = f"<b>{char.name}</b>: {char.description}"
                    story_elements.append(
                        Paragraph(char_text, styles['text'])
                    )
                story_elements.append(PageBreak())
            
            # Scenes
            for i, scene in enumerate(story.scenes):
                # Scene title
                story_elements.append(
                    Paragraph(scene.title, styles['scene_title'])
                )
                
                # Scene image
                if request.include_images and str(i) in request.images:
                    img_element = self._process_pdf_image(
                        request.images[str(i)], i
                    )
                    if img_element:
                        story_elements.append(img_element)
                        story_elements.append(Spacer(1, 0.25 * inch))
                
                # Scene text
                story_elements.append(
                    Paragraph(scene.text, styles['text'])
                )
                
                # Page break between scenes
                if i < len(story.scenes) - 1:
                    story_elements.append(PageBreak())
            
            # Build PDF
            doc.build(story_elements)
            
            # Clean up temp images
            self._cleanup_temp_images(len(story.scenes))
            
            logger.info(f"PDF exported: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return None
    
    def _export_html(self, story: Story, request: ExportRequest) -> Optional[str]:
        """Export story as HTML"""
        try:
            filename = request.filename or f"story_{story.story_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(config.OUTPUT_FOLDER, filename)
            
            html_content = self._generate_html(story, request)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML exported: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            return None
    
    def _export_json(self, story: Story, request: ExportRequest) -> Optional[str]:
        """Export story as JSON"""
        try:
            filename = request.filename or f"story_{story.story_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(config.OUTPUT_FOLDER, filename)
            
            export_data = {
                "story": story.to_dict(),
                "images": request.images if request.include_images else {},
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "format": "json"
                } if request.include_metadata else {}
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON exported: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return None
    
    def _get_pdf_styles(self) -> Dict:
        """Get PDF paragraph styles"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#6366f1'),
                spaceAfter=30,
                alignment=TA_CENTER
            ),
            'heading': ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=HexColor('#8b5cf6'),
                spaceAfter=12
            ),
            'scene_title': ParagraphStyle(
                'SceneTitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=HexColor('#8b5cf6'),
                spaceAfter=12,
                alignment=TA_CENTER
            ),
            'text': ParagraphStyle(
                'StoryText',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=18
            ),
            'meta': ParagraphStyle(
                'MetaText',
                parent=styles['Normal'],
                fontSize=10,
                textColor=HexColor('#6b7280'),
                alignment=TA_CENTER
            )
        }
        
        return custom_styles
    
    def _process_pdf_image(self, img_path: str, index: int) -> Optional[Image]:
        """Process image for PDF inclusion"""
        try:
            if img_path.startswith('data:image'):
                # Handle base64 image
                img_data = img_path.split(',')[1]
                img = PILImage.open(BytesIO(base64.b64decode(img_data)))
                temp_path = os.path.join(config.OUTPUT_FOLDER, f"temp_img_{index}.png")
                img.save(temp_path)
                img_path = temp_path
            elif img_path.startswith('http'):
                # Skip remote images for now
                return None
            
            if os.path.exists(img_path):
                return Image(img_path, width=5*inch, height=3*inch)
            
            return None
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return None
    
    def _cleanup_temp_images(self, count: int):
        """Remove temporary images after PDF generation"""
        for i in range(count):
            temp_path = os.path.join(config.OUTPUT_FOLDER, f"temp_img_{i}.png")
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _generate_html(self, story: Story, request: ExportRequest) -> str:
        """Generate HTML content for story"""
        
        # Convert images to base64 if needed
        embedded_images = {}
        if request.include_images:
            for key, img_path in request.images.items():
                if not img_path.startswith('data:'):
                    embedded_images[key] = self._image_to_base64(img_path)
                else:
                    embedded_images[key] = img_path
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{story.title}</title>
    {self._get_html_styles()}
</head>
<body>
    <div class="container">
        <header>
            <h1>{story.title}</h1>
            <p class="meta">Genre: {story.genre} | Age Group: {story.age_group}</p>
        </header>
        
        <section class="characters">
            <h2>Characters</h2>
            {''.join([f'<div class="character"><strong>{c.name}:</strong> {c.description}</div>' 
                     for c in story.characters])}
        </section>
        
        <div class="scenes">
            {''.join([self._generate_scene_html(scene, i, embedded_images.get(str(i))) 
                     for i, scene in enumerate(story.scenes)])}
        </div>
        
        <footer>
            <p>Generated with AI Storybook Generator</p>
            <p>{datetime.now().strftime('%B %d, %Y')}</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_scene_html(self, scene, index: int, image_data: Optional[str]) -> str:
        """Generate HTML for a single scene"""
        image_html = ''
        if image_data:
            image_html = f'<img src="{image_data}" alt="Scene {index + 1}" class="scene-image">'
        
        return f"""
        <div class="scene">
            <h3>{scene.title}</h3>
            {image_html}
            <p class="scene-text">{scene.text}</p>
        </div>
        """
    
    def _get_html_styles(self) -> str:
        """Get HTML style definitions"""
        return """
    <style>
        body {
            font-family: 'Georgia', serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #6366f1;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        h2 {
            color: #8b5cf6;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }
        h3 {
            color: #8b5cf6;
            text-align: center;
            font-size: 1.5rem;
            margin-top: 40px;
        }
        .meta {
            text-align: center;
            color: #6b7280;
            font-style: italic;
        }
        .characters {
            background: #f3f4f6;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
        }
        .character {
            margin-bottom: 10px;
        }
        .scene {
            margin-bottom: 50px;
            page-break-after: always;
        }
        .scene-image {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            display: block;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .scene-text {
            text-align: justify;
            font-size: 16px;
            line-height: 1.8;
        }
        footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
        }
        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
            }
        }
    </style>
        """
    
    def _image_to_base64(self, img_path: str) -> str:
        """Convert image file to base64 data URL"""
        try:
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{img_data}"
        except Exception as e:
            logger.error(f"Image encoding failed: {e}")
        
        return ""