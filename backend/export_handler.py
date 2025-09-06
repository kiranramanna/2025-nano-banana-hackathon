#!/usr/bin/env python3
"""
Export handler for generating PDFs and ePubs from stories
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from PIL import Image as PILImage
import base64
from io import BytesIO

class StoryExporter:
    def __init__(self, output_dir="../output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def export_to_pdf(self, story_data, images_data, filename=None):
        """Export story to PDF format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"story_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#6366f1'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        scene_title_style = ParagraphStyle(
            'SceneTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=HexColor('#8b5cf6'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        text_style = ParagraphStyle(
            'StoryText',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=18
        )
        
        story.append(Paragraph(story_data.get('title', 'Untitled Story'), title_style))
        story.append(Spacer(1, 0.5 * inch))
        
        if 'characters' in story_data:
            story.append(Paragraph("Characters", styles['Heading2']))
            for char in story_data['characters']:
                char_text = f"<b>{char['name']}</b>: {char['description']}"
                story.append(Paragraph(char_text, text_style))
            story.append(PageBreak())
        
        for i, scene in enumerate(story_data.get('scenes', [])):
            story.append(Paragraph(scene.get('title', f'Scene {i+1}'), scene_title_style))
            
            if str(i) in images_data:
                try:
                    img_path = images_data[str(i)]
                    if img_path.startswith('data:image'):
                        img_data = img_path.split(',')[1]
                        img = PILImage.open(BytesIO(base64.b64decode(img_data)))
                        temp_path = os.path.join(self.output_dir, f"temp_img_{i}.png")
                        img.save(temp_path)
                        img_path = temp_path
                    
                    if os.path.exists(img_path):
                        img = Image(img_path, width=5*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.25 * inch))
                except Exception as e:
                    print(f"Error adding image: {e}")
            
            story.append(Paragraph(scene.get('text', ''), text_style))
            
            if i < len(story_data['scenes']) - 1:
                story.append(PageBreak())
        
        doc.build(story)
        
        for i in range(len(story_data.get('scenes', []))):
            temp_path = os.path.join(self.output_dir, f"temp_img_{i}.png")
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return filepath
    
    def export_to_html(self, story_data, images_data, filename=None):
        """Export story as standalone HTML"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"story_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{story_data.get('title', 'AI Generated Story')}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #6366f1;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #8b5cf6;
            text-align: center;
            font-size: 1.8rem;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        .scene {{
            margin-bottom: 50px;
            page-break-after: always;
        }}
        .scene-image {{
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            display: block;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .scene-text {{
            line-height: 1.8;
            font-size: 18px;
            text-align: justify;
            color: #333;
        }}
        .characters {{
            background: #f3f4f6;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .character {{
            margin-bottom: 15px;
        }}
        .character-name {{
            font-weight: bold;
            color: #6366f1;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{story_data.get('title', 'Untitled Story')}</h1>
"""
        
        if 'characters' in story_data:
            html_content += '<div class="characters"><h3>Characters</h3>'
            for char in story_data['characters']:
                html_content += f'''
                <div class="character">
                    <span class="character-name">{char['name']}:</span> {char['description']}
                </div>'''
            html_content += '</div>'
        
        for i, scene in enumerate(story_data.get('scenes', [])):
            html_content += f'''
            <div class="scene">
                <h2>{scene.get('title', f'Scene {i+1}')}</h2>'''
            
            if str(i) in images_data:
                img_src = images_data[str(i)]
                if not img_src.startswith('data:'):
                    if os.path.exists(img_src):
                        with open(img_src, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode()
                            img_src = f"data:image/png;base64,{img_data}"
                
                html_content += f'<img class="scene-image" src="{img_src}" alt="Scene {i+1}">'
            
            html_content += f'''
                <p class="scene-text">{scene.get('text', '')}</p>
            </div>'''
        
        html_content += """
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def export_to_json(self, story_data, images_data, filename=None):
        """Export story as JSON for backup/sharing"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"story_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        export_data = {
            "story": story_data,
            "images": images_data,
            "exported_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filepath