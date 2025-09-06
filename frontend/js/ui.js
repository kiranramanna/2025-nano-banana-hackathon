/**
 * UI Controller Module
 */

class UIController {
    constructor() {
        this.elements = this.cacheElements();
        this.initializeUI();
    }
    
    cacheElements() {
        return {
            // Forms
            storyForm: document.getElementById('story-form'),
            storyPrompt: document.getElementById('story-prompt'),
            ageGroup: document.getElementById('age-group'),
            genre: document.getElementById('genre'),
            artStyle: document.getElementById('art-style'),
            numScenes: document.getElementById('num-scenes'),
            
            // Sections
            storyInput: document.getElementById('story-input'),
            characterSetup: document.getElementById('character-setup'),
            storyDisplay: document.getElementById('story-display'),
            exportOptions: document.getElementById('export-options'),
            savedStories: document.getElementById('saved-stories'),
            
            // Story display
            storyTitle: document.getElementById('story-title'),
            sceneCounter: document.getElementById('scene-counter'),
            sceneTitle: document.getElementById('scene-title'),
            sceneContent: document.getElementById('scene-content'),
            sceneImg: document.getElementById('scene-img'),
            
            // Buttons
            generateBtn: document.getElementById('generate-btn'),
            lockCharacters: document.getElementById('lock-characters'),
            prevScene: document.getElementById('prev-scene'),
            nextScene: document.getElementById('next-scene'),
            regenerateImage: document.getElementById('regenerate-image'),
            playNarration: document.getElementById('play-narration'),
            
            // Export buttons
            exportPDF: document.getElementById('export-pdf'),
            exportHTML: document.getElementById('export-html'),
            exportWeb: document.getElementById('export-web'),
            saveProject: document.getElementById('save-project'),
            
            // Overlays
            loadingOverlay: document.getElementById('loading-overlay'),
            loadingMessage: document.getElementById('loading-message'),
            errorModal: document.getElementById('error-modal'),
            errorMessage: document.getElementById('error-message'),
            
            // Lists
            characterForms: document.getElementById('character-forms'),
            storiesList: document.getElementById('stories-list')
        };
    }
    
    initializeUI() {
        // Set default values
        this.elements.ageGroup.value = Config.defaults.ageGroup;
        this.elements.genre.value = Config.defaults.genre;
        this.elements.artStyle.value = Config.defaults.artStyle;
        this.elements.numScenes.value = Config.defaults.numScenes;
    }
    
    // Section visibility
    showSection(sectionName) {
        const sections = [
            'storyInput',
            'characterSetup',
            'storyDisplay',
            'exportOptions'
        ];
        
        sections.forEach(section => {
            if (this.elements[section]) {
                this.elements[section].classList.toggle('hidden', section !== sectionName);
            }
        });
    }
    
    showMultipleSections(...sectionNames) {
        const sections = [
            'storyInput',
            'characterSetup',
            'storyDisplay',
            'exportOptions'
        ];
        
        sections.forEach(section => {
            if (this.elements[section]) {
                const shouldShow = sectionNames.includes(section);
                this.elements[section].classList.toggle('hidden', !shouldShow);
            }
        });
    }
    
    // Loading states
    showLoading(message = 'Loading...') {
        this.elements.loadingMessage.textContent = message;
        this.elements.loadingOverlay.classList.remove('hidden');
    }
    
    hideLoading() {
        this.elements.loadingOverlay.classList.add('hidden');
    }
    
    // Error handling
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorModal.classList.remove('hidden');
    }
    
    hideError() {
        this.elements.errorModal.classList.add('hidden');
    }
    
    // Form helpers
    getStoryFormData() {
        return {
            prompt: this.elements.storyPrompt.value.trim(),
            age_group: this.elements.ageGroup.value,
            genre: this.elements.genre.value,
            num_scenes: parseInt(this.elements.numScenes.value),
            art_style: this.elements.artStyle.value
        };
    }
    
    clearStoryForm() {
        this.elements.storyPrompt.value = '';
        this.elements.numScenes.value = Config.defaults.numScenes;
    }
    
    // Character forms
    createCharacterForm(character, index) {
        const form = document.createElement('div');
        form.className = 'character-form';
        form.innerHTML = `
            <h4>${character.name}</h4>
            <p>${character.description}</p>
            <div class="form-group">
                <label>Additional Visual Details (optional):</label>
                <textarea id="char-detail-${index}" rows="2" 
                    placeholder="e.g., always wears red goggles, has a star tattoo"></textarea>
            </div>
        `;
        return form;
    }
    
    displayCharacters(characters) {
        this.elements.characterForms.innerHTML = '';
        characters.forEach((character, index) => {
            const form = this.createCharacterForm(character, index);
            this.elements.characterForms.appendChild(form);
        });
    }
    
    getCharacterDetails() {
        const details = [];
        const textareas = this.elements.characterForms.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            details.push(textarea.value.trim());
        });
        return details;
    }
    
    // Story display
    displayStory(story) {
        this.elements.storyTitle.textContent = story.title;
    }
    
    displayScene(scene, sceneIndex, totalScenes) {
        this.elements.sceneCounter.textContent = 
            `Scene ${sceneIndex + 1} of ${totalScenes}`;
        this.elements.sceneTitle.textContent = scene.title;
        this.elements.sceneContent.textContent = scene.text;
        
        // Update navigation buttons
        this.elements.prevScene.disabled = sceneIndex === 0;
        this.elements.nextScene.disabled = sceneIndex === totalScenes - 1;
    }
    
    displaySceneImage(imageUrl) {
        if (imageUrl) {
            this.elements.sceneImg.src = imageUrl;
            this.showImageLoaded();
        } else {
            this.showImageLoading();
        }
    }
    
    showImageLoading() {
        this.elements.sceneImg.src = '';
        const loadingDiv = document.querySelector('.image-loading');
        if (loadingDiv) {
            loadingDiv.classList.remove('hidden');
        }
    }
    
    showImageLoaded() {
        const loadingDiv = document.querySelector('.image-loading');
        if (loadingDiv) {
            loadingDiv.classList.add('hidden');
        }
    }
    
    // Story list
    displayStoriesList(stories) {
        if (!stories || stories.length === 0) {
            this.elements.storiesList.innerHTML = 
                '<p style="color: #6b7280;">No saved stories yet</p>';
            return;
        }
        
        this.elements.storiesList.innerHTML = '';
        stories.forEach(story => {
            const card = this.createStoryCard(story);
            this.elements.storiesList.appendChild(card);
        });
    }
    
    createStoryCard(story) {
        const card = document.createElement('div');
        card.className = 'story-card';
        card.dataset.storyId = story.id || story.story_id;
        
        const date = story.created_at ? 
            new Date(story.created_at).toLocaleDateString() : 
            'Unknown date';
        
        card.innerHTML = `
            <h4>${story.title}</h4>
            <p>${story.num_scenes || story.scenes?.length || 0} scenes</p>
            <p style="font-size: 12px; margin-top: 5px;">${date}</p>
        `;
        
        return card;
    }
    
    // Validation
    validateStoryForm() {
        const data = this.getStoryFormData();
        const errors = [];
        
        if (!data.prompt) {
            errors.push('Please enter a story idea');
        } else if (data.prompt.length < Config.validation.minPromptLength) {
            errors.push(`Story idea must be at least ${Config.validation.minPromptLength} characters`);
        }
        
        if (data.num_scenes < Config.validation.minScenes || 
            data.num_scenes > Config.validation.maxScenes) {
            errors.push(`Number of scenes must be between ${Config.validation.minScenes} and ${Config.validation.maxScenes}`);
        }
        
        return errors;
    }
    
    // Utility
    setButtonLoading(button, isLoading, loadingText = 'Loading...') {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = loadingText;
        } else {
            button.disabled = false;
            if (button.dataset.originalText) {
                button.textContent = button.dataset.originalText;
            }
        }
    }
}