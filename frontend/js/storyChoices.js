class StoryChoices {
    constructor() {
        this.currentChoices = [];
        this.isLoading = false;
        this.listenersInitialized = false;
    }

    init() {
        if (!this.listenersInitialized) {
            this.setupEventListeners();
            this.listenersInitialized = true;
        }
    }

    setupEventListeners() {
        // Use event delegation for dynamically loaded choice cards
        document.addEventListener('click', (e) => {
            const choiceCard = e.target.closest('.choice-card');
            if (choiceCard) {
                // Find the index of the clicked card
                const allCards = document.querySelectorAll('.choice-card');
                const index = Array.from(allCards).indexOf(choiceCard);
                if (index !== -1) {
                    this.selectChoice(index);
                }
            }
        });
    }

    async generateChoices(currentPageIndex) {
        console.log('Generating choices for page:', currentPageIndex);
        if (this.isLoading) return;
        
        this.isLoading = true;
        const storyData = window.bookViewer?.storyData;
        
        // Always generate default choices first, then try to get custom ones
        this.generateDefaultChoices(storyData?.scenes[currentPageIndex]);
        
        if (!storyData) {
            console.log('No story data available, using default choices');
            this.isLoading = false;
            return;
        }

        try {
            // Get current scene context
            const currentScene = storyData.scenes[currentPageIndex];
            const storyContext = {
                title: storyData.title,
                currentScene: currentScene,
                pageNumber: currentPageIndex + 1,
                totalPages: storyData.scenes.length,
                genre: document.getElementById('genre')?.value,
                ageGroup: document.getElementById('age-group')?.value
            };

            // Request story choices from backend
            const response = await window.api?.getStoryChoices(storyContext);
            
            if (response && response.choices) {
                this.currentChoices = response.choices;
                this.displayChoices(response.choices);
            } else {
                // Generate default choices if API fails
                console.log('API did not return choices, using defaults');
                this.generateDefaultChoices(currentScene);
            }
        } catch (error) {
            console.error('Failed to generate story choices:', error);
            this.generateDefaultChoices(storyData.scenes[currentPageIndex]);
        } finally {
            this.isLoading = false;
        }
    }

    generateDefaultChoices(currentScene) {
        // Default choices when API is not available
        const defaultChoices = [
            {
                title: 'Original Path',
                description: 'Continue with the main storyline',
                icon: '📖',
                type: 'original'
            },
            {
                title: 'Magical Twist',
                description: 'Add a magical element to the story',
                icon: '✨',
                type: 'magical'
            },
            {
                title: 'Surprise Turn',
                description: 'Introduce an unexpected twist',
                icon: '🎭',
                type: 'surprise'
            },
            {
                title: 'Adventure Path',
                description: 'Take the story on an adventure',
                icon: '🚀',
                type: 'adventure'
            }
        ];

        this.currentChoices = defaultChoices;
        this.displayChoices(defaultChoices);
    }

    displayChoices(choices) {
        console.log('Displaying choices:', choices);
        const choiceCards = document.querySelectorAll('.choice-card');
        console.log('Found choice cards:', choiceCards.length);
        
        choices.forEach((choice, index) => {
            if (choiceCards[index]) {
                const card = choiceCards[index];
                const icon = card.querySelector('.choice-icon');
                const title = card.querySelector('h4');
                const description = card.querySelector('.choice-description');
                
                if (icon) icon.textContent = choice.icon || this.getDefaultIcon(index);
                if (title) title.textContent = choice.title;
                if (description) description.textContent = choice.description;
                
                // Store choice data
                card.dataset.choiceData = JSON.stringify(choice);
            }
        });

        // Show the choices container
        const choicesContainer = document.getElementById('story-choices');
        if (choicesContainer) {
            choicesContainer.classList.remove('hidden');
            console.log('Choices container shown');
        }
    }

    getDefaultIcon(index) {
        const icons = ['📖', '✨', '🎭', '🚀'];
        return icons[index] || '📖';
    }

    async selectChoice(choiceIndex) {
        console.log('Choice selected:', choiceIndex, this.currentChoices);
        
        if (this.isLoading || !this.currentChoices[choiceIndex]) {
            console.log('Choice blocked - isLoading:', this.isLoading, 'Choice exists:', !!this.currentChoices[choiceIndex]);
            return;
        }
        
        const selectedChoice = this.currentChoices[choiceIndex];
        this.isLoading = true;
        
        // Show full-screen loading overlay
        this.showLoadingOverlay(selectedChoice);
        
        // Show loading state on the button
        this.showChoiceLoading(choiceIndex);
        
        try {
            const storyData = window.bookViewer?.storyData;
            const currentPage = window.bookViewer?.currentPage || 0;
            
            // Prepare request data
            const requestData = {
                storyId: storyData.id,
                currentPage: currentPage,
                choice: selectedChoice,
                storyContext: {
                    title: storyData.title,
                    scenes: storyData.scenes,
                    genre: document.getElementById('genre')?.value,
                    ageGroup: document.getElementById('age-group')?.value,
                    artStyle: document.getElementById('art-style')?.value
                }
            };

            // Request new scene based on choice
            const response = await window.api?.generateSceneFromChoice(requestData);
            
            if (response && response.scene) {
                console.log('New scene generated:', response);
                
                // Add new scene to story
                const newScene = response.scene.scene || response.scene;
                window.bookViewer?.addSceneToStory(newScene);

                // Update loading message for image generation
                this.updateLoadingMessage('Generating magical illustration...');
                
                // Generate image for the new scene
                if (window.app?.generateSceneImage) {
                    try {
                        const newSceneIndex = window.bookViewer?.storyData.scenes.length - 1;
                        await window.app.generateSceneImage(newSceneIndex);
                    } catch (e) {
                        console.warn('Image generation failed:', e);
                    }
                }

                // Hide choices and loading overlay
                this.hideChoices();
                this.hideLoadingOverlay();
                
                // Navigate to the new page
                window.bookViewer?.nextPage();

                // Check if we should show choices on the next page
                const isLastScene = response.is_final || response.scenes_remaining === 0;
                if (!isLastScene) {
                    // Choices will be shown by displayPage logic
                }
            } else {
                // Use default scene generation
                this.generateDefaultScene(selectedChoice);
            }
        } catch (error) {
            console.error('Failed to generate scene from choice:', error);
            this.hideLoadingOverlay();
            window.ui?.showError('Failed to continue story. Please try again.');
        } finally {
            this.isLoading = false;
            this.hideChoiceLoading(choiceIndex);
            this.hideLoadingOverlay();
        }
    }

    generateDefaultScene(choice) {
        // Create a default scene when API is not available
        const defaultScene = {
            scene_number: window.bookViewer.currentPage + 2,
            title: `Chapter ${window.bookViewer.currentPage + 2}`,
            text: this.generateDefaultContent(choice),
            content: this.generateDefaultContent(choice),
            image_prompt: 'A magical storybook scene',
            image_url: null,
            characters_present: []
        };
        
        window.bookViewer?.addSceneToStory(defaultScene);
        this.hideChoices();
        this.hideLoadingOverlay();
        
        // Navigate to the new page
        setTimeout(() => {
            window.bookViewer?.nextPage();
        }, 500);
    }

    generateDefaultContent(choice) {
        const templates = {
            'original': 'The story continues as planned, with our heroes moving forward on their journey...',
            'magical': 'Suddenly, a burst of magical energy filled the air, transforming everything around them...',
            'surprise': 'To everyone\'s surprise, an unexpected visitor arrived with important news...',
            'adventure': 'The path ahead led to an exciting new adventure, full of challenges and discoveries...'
        };
        
        return templates[choice.type] || templates['original'];
    }

    showChoiceLoading(choiceIndex) {
        const choiceCards = document.querySelectorAll('.choice-card');
        if (choiceCards[choiceIndex]) {
            const card = choiceCards[choiceIndex];
            card.style.opacity = '0.5';
            card.style.pointerEvents = 'none';
            
            // Add loading spinner
            const spinner = document.createElement('div');
            spinner.className = 'choice-loading-spinner';
            spinner.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 30px;
                height: 30px;
                border: 3px solid #e5e7eb;
                border-top: 3px solid #6366f1;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            `;
            card.appendChild(spinner);
        }
    }

    hideChoiceLoading(choiceIndex) {
        const choiceCards = document.querySelectorAll('.choice-card');
        if (choiceCards[choiceIndex]) {
            const card = choiceCards[choiceIndex];
            card.style.opacity = '1';
            card.style.pointerEvents = 'auto';
            
            // Remove loading spinner
            const spinner = card.querySelector('.choice-loading-spinner');
            if (spinner) spinner.remove();
        }
    }

    hideChoices() {
        const choicesContainer = document.getElementById('story-choices');
        if (choicesContainer) {
            choicesContainer.classList.add('hidden');
        }
        this.currentChoices = [];
    }

    // Helper method to check if we should show choices
    shouldShowChoices(currentPage, totalPages) {
        // Show choices before each new scene except the last one
        return currentPage < totalPages - 1;
    }
    
    showLoadingOverlay(choice) {
        const overlay = document.getElementById('loading-overlay');
        const message = document.getElementById('loading-message');
        
        if (overlay) {
            overlay.classList.remove('hidden');
            
            // Set custom message based on choice
            if (message) {
                const messages = {
                    'original': 'Continuing your adventure...',
                    'magical': 'Adding a touch of magic...',
                    'surprise': 'Creating an unexpected twist...',
                    'adventure': 'Embarking on a new path...'
                };
                message.textContent = messages[choice.type] || 'Creating your next chapter...';
            }
        }
    }
    
    updateLoadingMessage(text) {
        const message = document.getElementById('loading-message');
        if (message) {
            message.textContent = text;
        }
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
}

// Initialize story choices
window.storyChoices = new StoryChoices();

// Initialize after components are loaded
window.addEventListener('componentsLoaded', () => {
    window.storyChoices.init();
});

// Also initialize on DOMContentLoaded as fallback
document.addEventListener('DOMContentLoaded', () => {
    window.storyChoices.init();
});
