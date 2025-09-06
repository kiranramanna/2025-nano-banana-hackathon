# 🎨 AI Storybook Generator - 2025 Nano Banana Hackathon

An AI-powered storybook generator that creates illustrated children's stories with consistent characters using Google's Gemini 2.5 Flash API. Transform simple story ideas into fully illustrated, narrated digital storybooks with multiple export options.

## ⚙️ Project Overview – "AI Storybook Generator"

```markdown
# 🧠 Concept
Input a story (typed, uploaded, or AI-generated) → Gemini generates illustrated scenes → Optional: ElevenLabs narrates story → Export as web app or downloadable eBook.
```

---

## 🛠️ MVP Features

````markdown
1. 📜 Story Input
   - Textbox for manual story input
   - OR button to generate a story via Gemini ("Generate story for a 7-year-old about a time-traveling squirrel")

2. 🧍 Character & Style Lock-In
   - Ask user to define main characters briefly
     (e.g. "A red robot named Max, always wearing goggles")
   - Style selector: “Cartoon,” “Watercolor,” “Pixel Art,” etc.
   - Store these inputs as a visual consistency anchor

3. 🖼️ Scene-by-Scene Illustration
   - Auto-chunk story into 5–8 scenes
   - For each chunk:
     - Prompt Gemini to generate a consistent image based on characters + scene
     - Use a system prompt like:
       ```
       Generate an image for this scene using the consistent characters defined earlier.
       Keep Max the red robot's goggles in every image.
       Scene: "Max activates the time machine and lands in a dinosaur jungle."
       Style: Watercolor
       ```
   - Cache scene images with index (e.g., `scene_1.jpg`, etc.)

4. 🔈 Narration (Bonus)
   - Pass story chunks to ElevenLabs API for TTS
   - Optionally allow user to pick voice/style
   - Add "play" button per page

5. 📘 Output Options
   - Scrollable web storybook
   - "Download as PDF" or ePub (use Puppeteer/Playwright to print HTML → PDF)
   - Optional: "Share your story" public link

6. 💻 Hosting
   - Use Gemini AI Studio or Cloud Run (free quota works fine for this)
   - UI: Streamlit or Flask + HTML template for simplicity

7. 🎥 Demo Video Plan
   - Show user typing prompt → generating story → images appear → user flips through them
   - Add short ElevenLabs narration to make it pop
   - Keep video under 2 minutes, show magic fast
````

---

## 🧠 Prompt Engineering – Gemini Image Calls

```python
# Example system + user prompt for consistency
system_prompt = """
You are a visual storyteller. Maintain character consistency across scenes.
Main Character: Max, a red robot with goggles
Style: Watercolor children's book
"""

user_prompt = """
Scene 3: Max activates the time machine and lands in a dinosaur jungle.
Keep Max’s appearance and style consistent with earlier images.
"""
```

---

## 🚀 Stack Recommendation

```markdown
- Backend: Python (Flask or FastAPI)
- Frontend: HTML + TailwindCSS or Streamlit (quickest)
- Gemini API: Text + Image generation
- ElevenLabs: TTS for story narration (optional)
- Hosting: Google Cloud Run, HuggingFace Spaces, or Replit (if fast)
```

---

## ✅ Gemini Integration Writeup (for submission)

```markdown
We use Gemini 2.5 Flash Image’s advanced character consistency and stylistic retention to create a sequentially illustrated storybook from user-provided or AI-generated text. Each scene is prompted with visual memory of characters and prior context, ensuring the main character retains appearance and personality throughout. Gemini’s dynamic image generation transforms plain stories into visually engaging narratives, a task not possible with traditional text-to-image models due to character drift.
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/2025-nano-banana-hackathon.git
cd 2025-nano-banana-hackathon
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

4. **Run the application**
```bash
python run.py
```

The backend will start on `http://localhost:5000` and the frontend will open in your browser.

## 🎯 Key Features Implemented

### Core Functionality
- ✅ **AI Story Generation** - Create engaging stories from simple prompts
- ✅ **Character Consistency** - Maintain character appearance across all scenes
- ✅ **Scene-by-Scene Illustration** - Generate unique images for each scene
- ✅ **Multiple Art Styles** - Watercolor, Cartoon, Pixel Art, Anime, Realistic
- ✅ **Age-Appropriate Content** - Stories tailored for different age groups
- ✅ **Export Options** - PDF, HTML, JSON formats

### Advanced Features
- ✅ **Character Refinement** - AI learns from first image to maintain consistency
- ✅ **Custom Image Prompts** - Regenerate scenes with specific requirements
- ✅ **Browser-Based Narration** - Text-to-speech for story playback
- ✅ **Local Storage** - Save and reload story projects
- ✅ **Responsive Design** - Works on desktop and mobile devices

## 📁 Project Structure

```
2025-nano-banana-hackathon/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration management
│   ├── models/             # Data models
│   │   ├── story.py        # Story, Scene, Character models
│   │   ├── image.py        # Image request/response models
│   │   └── export.py       # Export request models
│   ├── services/           # Business logic
│   │   ├── gemini_client.py    # Gemini API wrapper
│   │   ├── story_service.py    # Story generation
│   │   ├── image_service.py    # Image generation
│   │   ├── cache_service.py    # Storage & caching
│   │   └── export_service.py   # Export functionality
│   ├── routes/             # API endpoints
│   │   ├── story_routes.py     # Story endpoints
│   │   ├── image_routes.py     # Image endpoints
│   │   ├── export_routes.py    # Export endpoints
│   │   └── health_routes.py    # Health checks
│   └── utils/              # Utilities
│       ├── validators.py        # Request validation
│       ├── error_handler.py     # Error handling
│       └── helpers.py           # Helper functions
├── frontend/
│   ├── index.html          # Main UI
│   ├── styles.css          # Styling
│   └── js/                 # Modular JavaScript
│       ├── config.js       # Configuration
│       ├── api.js          # API service
│       ├── ui.js           # UI controller
│       ├── storage.js      # Local storage
│       ├── narrator.js     # Text-to-speech
│       └── app.js          # Main app controller
├── public/
│   ├── images/             # Generated images
│   └── stories/            # Story data
├── output/                 # Exported files
├── requirements.txt        # Python dependencies
├── .env                    # API keys (create from .env.example)
├── run.py                  # Main launcher script
└── README.md              # This file
```

## 🔧 API Endpoints

### Story Generation
- `POST /api/generate-story` - Generate a new story from prompt
- `GET /api/get-story/<story_id>` - Retrieve story data
- `GET /api/stories` - List all generated stories

### Image Generation
- `POST /api/generate-scene-image` - Create illustration for a scene
- `POST /api/refine-character` - Refine character consistency

### Export
- `POST /api/export/pdf` - Export story as PDF
- `POST /api/export/html` - Export as standalone HTML
- `POST /api/export/json` - Export story data as JSON

## 🎨 How It Works

1. **Story Input**: User provides a story idea or prompt
2. **AI Generation**: Gemini 2.5 Flash creates a structured story with:
   - Title and characters
   - Scene-by-scene breakdown
   - Detailed character descriptions
3. **Character Lock-In**: User can refine character details for consistency
4. **Scene Illustration**: Each scene gets a unique AI-generated image
5. **Character Consistency**: System maintains visual consistency across scenes
6. **Export & Share**: Download as PDF, HTML, or share online

## 🧠 Gemini Integration Details

The project leverages Gemini 2.5 Flash's advanced capabilities:

- **Text Generation**: Creates engaging, age-appropriate stories
- **Image Generation**: Uses Imagen 3.0 for high-quality illustrations
- **Character Consistency**: Maintains visual continuity across scenes
- **Style Retention**: Preserves chosen art style throughout the story

### Prompt Engineering

```python
# Example character consistency prompt
prompt = f"""
Style: {style}
Scene: {scene['image_prompt']}
Characters: {', '.join(characters_in_scene)}

IMPORTANT: Maintain consistent character appearance throughout. 
The characters should look exactly as described in their visual descriptions.
"""
```

## 🏆 Hackathon Submission

### Innovation Points
1. **Character Consistency**: Novel approach to maintaining visual continuity
2. **Multi-Modal Generation**: Combines text and image generation seamlessly
3. **Educational Focus**: Age-appropriate content generation
4. **Export Flexibility**: Multiple output formats for different use cases

### Technical Achievements
- Real-time image generation with Gemini API
- Frontend-backend architecture for scalability
- Local storage for offline functionality
- Responsive design for cross-device compatibility

## 🔮 Future Enhancements

- [ ] ElevenLabs integration for professional narration
- [ ] Multi-language support
- [ ] Collaborative story creation
- [ ] Animation between scenes
- [ ] Mobile app version
- [ ] Social sharing features
- [ ] Story templates library
- [ ] Voice-to-story input

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- Google Gemini team for the powerful AI APIs
- 2025 Nano Banana Hackathon organizers
- Open source community for the amazing tools

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for the 2025 Nano Banana Hackathon**
