/**
 * Main Application Controller
 */

class StoryBookApp {
    constructor() {
        // Initialize services
        this.api = new APIService();
        this.ui = new UIController();
        this.storage = new StorageService();
        this.narrator = new NarrationService();
        
        // Application state
        this.state = {
            currentStory: null,
            currentSceneIndex: 0,
            sceneImages: {},
            isGenerating: false,
            isNarrating: false
        };
        
        // Initialize
        this.init();
    }
    
    async init() {
        // Check API health
        await this.checkAPIHealth();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load saved stories
        this.loadSavedStories();
        
        // Load user preferences
        this.loadPreferences();
        
        // Setup auto-save
        this.setupAutoSave();
    }
    
    async checkAPIHealth() {
        try {
            const health = await this.api.checkHealth();
            console.log('API Health:', health);
        } catch (error) {
            this.ui.showError('Cannot connect to backend. Please ensure the server is running.');
        }
    }
    
    setupEventListeners() {
        // Story generation
        this.ui.elements.storyForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleGenerateStory();
        });
        
        // Character setup
        this.ui.elements.lockCharacters.addEventListener('click', () => {
            this.handleLockCharacters();
        });
        
        // Error modal
        document.querySelector('.close')?.addEventListener('click', () => {
            this.ui.hideError();
        });
        
        document.getElementById('error-close')?.addEventListener('click', () => {
            this.ui.hideError();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }
    
    // Story Generation
    async handleGenerateStory() {
        // Validate form
        const errors = this.ui.validateStoryForm();
        if (errors.length > 0) {
            this.ui.showError(errors.join('\n'));
            return;
        }
        
        // Get form data
        const formData = this.ui.getStoryFormData();
        
        // Set generating state
        this.state.isGenerating = true;
        this.ui.showLoading('Creating your magical story...');
        this.ui.setButtonLoading(this.ui.elements.generateBtn, true, 'Generating...');
        
        try {
            // Generate story
            const response = await this.api.generateStory(formData);
            
            // Update state
            this.state.currentStory = response.story;
            this.state.currentStory.id = response.story_id;
            this.state.currentSceneIndex = 0;
            this.state.sceneImages = {};
            
            // Show character setup
            this.ui.hideLoading();
            this.ui.showSection('characterSetup');
            this.ui.displayCharacters(this.state.currentStory.characters);
            
        } catch (error) {
            this.ui.showError('Failed to generate story: ' + error.message);
        } finally {
            this.state.isGenerating = false;
            this.ui.hideLoading();
            this.ui.setButtonLoading(this.ui.elements.generateBtn, false);
        }
    }
    
    // Character Management
    async handleLockCharacters() {
        // Get additional character details
        const details = this.ui.getCharacterDetails();
        
        // Update characters with additional details
        this.state.currentStory.characters.forEach((char, index) => {
            if (details[index]) {
                char.visual_description += ' ' + details[index];
            }
        });
        
        // Generate initial scene images
        this.ui.showLoading('Generating first page illustration...');
        
        try {
            // Generate first scene image
            await this.generateSceneImage(0);
            
            // Format story data for book viewer
            const storyData = {
                id: this.state.currentStory.id,
                title: this.state.currentStory.title,
                characters: this.state.currentStory.characters,
                scenes: this.state.currentStory.scenes.map((scene, index) => ({
                    title: scene.title,
                    content: scene.text,
                    image: this.state.sceneImages[index] || null
                }))
            };
            
            // Open book viewer
            window.bookViewer?.openBookViewer(storyData);

            // Lazy image generation: do NOT pre-generate remaining scene images.
            // Next scene images will be generated only after the user makes a
            // selection in "What happens next?" via the choices flow.
            console.log('Lazy image mode: deferring next scene images until choice selection');
            
        } catch (error) {
            this.ui.showError('Failed to start story: ' + error.message);
        } finally {
            this.ui.hideLoading();
        }
    }
    
    // Image Generation
    async generateSceneImage(sceneIndex) {
        const scene = this.state.currentStory.scenes[sceneIndex];
        
        try {
            const response = await this.api.generateSceneImage({
                story_id: this.state.currentStory.id,
                scene_number: scene.scene_number,
                style: this.state.currentStory.style || 'watercolor',
                aspect_ratio: '16:9'
            });
            
            if (response.success) {
                const imageUrl = `${Config.IMAGE_BASE_URL}${response.image_url}`;
                this.state.sceneImages[sceneIndex] = imageUrl;
                
                // Update book viewer if scene is displayed
                if (window.bookViewer?.storyData) {
                    window.bookViewer.storyData.scenes[sceneIndex].image = imageUrl;
                    if (window.bookViewer.currentPage === sceneIndex) {
                        document.getElementById('page-image').src = imageUrl;
                    }
                }
                
                return imageUrl;
            }
        } catch (error) {
            console.error('Failed to generate image for scene', sceneIndex, error);
        }
    }
    
    async generateRemainingImages() {
        // Generate remaining scene images in background
        for (let i = 1; i < this.state.currentStory.scenes.length; i++) {
            await this.generateSceneImage(i);
        }
    }
    
    // Storage Functions
    loadSavedStories() {
        const stories = this.storage.getAllStories();
        const storiesList = stories.map(item => ({
            ...item.story,
            created_at: item.timestamp
        }));
        this.ui.displayStoriesList(storiesList);
        
        // Add click handlers for story cards
        document.getElementById('stories-list')?.addEventListener('click', (e) => {
            const card = e.target.closest('.story-card');
            if (card) {
                this.handleLoadStory(card.dataset.storyId);
            }
        });
    }
    
    handleLoadStory(storyId) {
        const data = this.storage.getStory(storyId);
        
        if (data) {
            this.state.currentStory = data.story;
            this.state.sceneImages = data.images || {};
            this.state.currentSceneIndex = 0;
            
            // Format story data for book viewer
            const storyData = {
                id: this.state.currentStory.id,
                title: this.state.currentStory.title,
                characters: this.state.currentStory.characters,
                scenes: this.state.currentStory.scenes.map((scene, index) => ({
                    title: scene.title,
                    content: scene.text,
                    image: this.state.sceneImages[index] || null
                }))
            };
            
            // Open book viewer
            window.bookViewer?.openBookViewer(storyData);
        }
    }
    
    // Preferences
    loadPreferences() {
        const prefs = this.storage.getPreferences();
        
        if (prefs.ageGroup) {
            document.getElementById('age-group').value = prefs.ageGroup;
        }
        if (prefs.genre) {
            document.getElementById('genre').value = prefs.genre;
        }
        if (prefs.artStyle) {
            document.getElementById('art-style').value = prefs.artStyle;
        }
    }
    
    savePreferences() {
        const prefs = {
            ageGroup: document.getElementById('age-group').value,
            genre: document.getElementById('genre').value,
            artStyle: document.getElementById('art-style').value,
            autoSave: true,
            narrationEnabled: true
        };
        
        this.storage.savePreferences(prefs);
    }
    
    // Auto-save
    setupAutoSave() {
        setInterval(() => {
            if (this.state.currentStory && !this.state.isGenerating) {
                this.storage.saveStory(
                    this.state.currentStory,
                    this.state.sceneImages
                );
            }
        }, Config.ui.autoSaveInterval || 30000);
    }
    
    // Keyboard shortcuts
    handleKeyboardShortcuts(event) {
        // Arrow keys for scene navigation in book viewer
        if (window.bookViewer?.storyData) {
            if (event.key === 'ArrowLeft') {
                window.bookViewer.previousPage();
            } else if (event.key === 'ArrowRight') {
                window.bookViewer.nextPage();
            } else if (event.key === ' ' && event.ctrlKey) {
                // Ctrl+Space for narration
                event.preventDefault();
                window.bookViewer.playNarration();
            } else if (event.key === 'f' && event.ctrlKey) {
                // Ctrl+F for fullscreen
                event.preventDefault();
                window.bookViewer.toggleFullscreen();
            }
        }
    }
}

// Initialize app when components are loaded
window.addEventListener('componentsLoaded', () => {
    window.app = new StoryBookApp();
});
