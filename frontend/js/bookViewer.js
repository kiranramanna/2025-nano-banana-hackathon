class BookViewer {
    constructor() {
        this.currentPage = 0;
        this.totalPages = 0;
        this.storyData = null;
        this.touchStartX = null;
        this.touchEndX = null;
        this.isTransitioning = false;
        this.selectedTheme = '';
        this.selectedAge = '';
    }

    init() {
        this.setupEventListeners();
        this.setupTouchGestures();
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('prev-page')?.addEventListener('click', () => this.previousPage());
        document.getElementById('next-page')?.addEventListener('click', () => this.nextPage());
        
        // Back button
        document.getElementById('back-to-setup')?.addEventListener('click', () => this.exitBookViewer());
        
        // Menu toggle
        document.getElementById('book-menu')?.addEventListener('click', () => this.toggleMenu());
        document.querySelector('.menu-close')?.addEventListener('click', () => this.closeMenu());
        
        // Menu options
        document.getElementById('restart-story')?.addEventListener('click', () => this.restartStory());
        document.getElementById('save-progress')?.addEventListener('click', () => this.saveProgress());
        
        // Quick actions
        document.getElementById('play-narration')?.addEventListener('click', () => this.playNarration());
        document.getElementById('regenerate-image')?.addEventListener('click', () => this.regenerateImage());
        document.getElementById('toggle-fullscreen')?.addEventListener('click', () => this.toggleFullscreen());
    }

    setupTouchGestures() {
        const bookPages = document.getElementById('book-pages');
        if (!bookPages) return;

        // Touch events for swipe gestures
        bookPages.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        });

        bookPages.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        });

        // Mouse events for desktop swipe simulation
        let mouseDown = false;
        bookPages.addEventListener('mousedown', (e) => {
            mouseDown = true;
            this.touchStartX = e.screenX;
        });

        bookPages.addEventListener('mouseup', (e) => {
            if (mouseDown) {
                this.touchEndX = e.screenX;
                this.handleSwipe();
                mouseDown = false;
            }
        });

        bookPages.addEventListener('mouseleave', () => {
            mouseDown = false;
        });
    }

    handleSwipe() {
        if (!this.touchStartX || !this.touchEndX) return;
        
        const swipeThreshold = 50;
        const diff = this.touchStartX - this.touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next page
                this.nextPage();
            } else {
                // Swipe right - previous page
                this.previousPage();
            }
        }
        
        this.touchStartX = null;
        this.touchEndX = null;
    }

    openBookViewer(storyData) {
        this.storyData = storyData;
        this.currentPage = 0;
        this.totalPages = storyData.scenes.length;
        
        // Get theme and age settings
        this.selectedTheme = document.getElementById('genre')?.value || 'fantasy';
        this.selectedAge = document.getElementById('age-group')?.value || '7-10';
        
        // Switch screens: hide setup, show viewer
        const setup = document.getElementById('setup-screen');
        const viewer = document.getElementById('book-viewer');
        if (setup) setup.classList.remove('active');
        if (viewer) {
            viewer.classList.remove('hidden');
            viewer.classList.add('active');
        }
        
        // Set title
        document.getElementById('story-title').textContent = storyData.title;
        
        // Show swipe hint for mobile
        if ('ontouchstart' in window) {
            this.showSwipeHint();
        }
        
        // Display first page
        this.displayPage(0);
    }

    displayPage(pageIndex) {
        if (pageIndex < 0 || pageIndex >= this.totalPages) return;
        
        const scene = this.storyData.scenes[pageIndex];
        const pageBackground = document.getElementById('page-background');
        const pageImage = document.getElementById('page-image');
        const pageTitle = document.getElementById('page-title');
        const pageContent = document.getElementById('page-content');
        
        // Apply theme and age classes
        pageBackground.className = `page-background theme-${this.getThemeClass()} age-${this.selectedAge}`;
        
        // Update content
        pageTitle.textContent = scene.title;
        pageContent.textContent = scene.content;
        
        // Load image
        if (scene.image) {
            this.showImageLoading(true);
            pageImage.src = scene.image;
            pageImage.onload = () => this.showImageLoading(false);
            pageImage.onerror = () => {
                this.showImageLoading(false);
                pageImage.src = '/images/placeholder.jpg';
            };
        }
        
        // Update page indicator
        document.getElementById('current-page-num').textContent = pageIndex + 1;
        document.getElementById('total-pages').textContent = this.totalPages;
        
        // Update navigation buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        if (prevBtn) prevBtn.disabled = pageIndex === 0;
        if (nextBtn) nextBtn.disabled = pageIndex === this.totalPages - 1;
        
        // Check if we should show story choices
        // Always show choices after the first page and any page that doesn't have a next scene yet
        const totalPlanned = this.storyData.total_planned_scenes || 5;
        const hasNextScene = this.storyData.scenes[pageIndex + 1] !== undefined;
        const isNotFinalScene = pageIndex < totalPlanned - 1;
        
        // Show choices if: we're on page 1 OR we don't have a next scene (and not at the final scene)
        if ((pageIndex === 0 || !hasNextScene) && isNotFinalScene) {
            console.log('Showing story choices on page', pageIndex + 1);
            this.showStoryChoices();
        } else {
            this.hideStoryChoices();
        }
        
        // Show PDF download if on last page
        if (pageIndex === this.totalPages - 1) {
            this.enablePDFDownload();
        }
    }

    getThemeClass() {
        const themeMap = {
            'fantasy': 'fantasy',
            'adventure': 'adventure',
            'science-fiction': 'scifi',
            'mystery': 'mystery',
            'comedy': 'comedy'
        };
        return themeMap[this.selectedTheme] || 'fantasy';
    }

    showImageLoading(show) {
        const loading = document.querySelector('.image-loading');
        if (loading) {
            loading.classList.toggle('hidden', !show);
        }
    }

    previousPage() {
        if (this.currentPage > 0 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.currentPage--;
            this.animatePageTurn('prev', () => {
                this.displayPage(this.currentPage);
                this.isTransitioning = false;
            });
        }
    }

    nextPage() {
        if (this.currentPage < this.totalPages - 1 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.currentPage++;
            this.animatePageTurn('next', () => {
                this.displayPage(this.currentPage);
                this.isTransitioning = false;
            });
        }
    }

    animatePageTurn(direction, callback) {
        const currentPageEl = document.getElementById('current-page');
        
        if (direction === 'next') {
            currentPageEl.style.animation = 'pageFlipOut 0.5s ease-in-out';
        } else {
            currentPageEl.style.animation = 'pageFlipIn 0.5s ease-in-out';
        }
        
        setTimeout(() => {
            currentPageEl.style.animation = '';
            callback();
        }, 500);
    }

    showStoryChoices() {
        const choicesContainer = document.getElementById('story-choices');
        if (choicesContainer) {
            choicesContainer.classList.remove('hidden');
            // Story choices will be populated by storyChoices.js
            window.storyChoices?.generateChoices(this.currentPage);
        }
    }

    hideStoryChoices() {
        const choicesContainer = document.getElementById('story-choices');
        if (choicesContainer) {
            choicesContainer.classList.add('hidden');
        }
    }

    showSwipeHint() {
        const hint = document.getElementById('swipe-hint');
        if (hint) {
            hint.classList.remove('hidden');
            setTimeout(() => {
                hint.classList.add('hidden');
            }, 3000);
        }
    }

    exitBookViewer() {
        const viewer = document.getElementById('book-viewer');
        const setup = document.getElementById('setup-screen');
        
        if (viewer) {
            viewer.classList.add('hidden');
            viewer.classList.remove('active');
        }
        
        if (setup) {
            setup.classList.remove('hidden');
            setup.classList.add('active');
        }
        
        this.currentPage = 0;
        this.storyData = null;
    }

    toggleMenu() {
        const menuOverlay = document.getElementById('book-menu-overlay');
        if (menuOverlay) {
            menuOverlay.classList.toggle('hidden');
        }
    }

    closeMenu() {
        const menuOverlay = document.getElementById('book-menu-overlay');
        if (menuOverlay) {
            menuOverlay.classList.add('hidden');
        }
    }

    restartStory() {
        this.currentPage = 0;
        this.displayPage(0);
        this.closeMenu();
        this.showStoryChoices();
    }

    saveProgress() {
        const progressData = {
            storyId: this.storyData.id,
            currentPage: this.currentPage,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('story-progress', JSON.stringify(progressData));
        this.closeMenu();
        
        // Show success message
        this.showNotification('Progress saved!');
    }

    playNarration() {
        const scene = this.storyData.scenes[this.currentPage];
        if (scene && scene.content) {
            window.narrator?.playText(scene.content);
        }
    }

    async regenerateImage() {
        const scene = this.storyData.scenes[this.currentPage];
        if (!scene) return;
        
        this.showImageLoading(true);
        
        try {
            const response = await window.api?.regenerateImage(
                this.storyData.id,
                this.currentPage
            );
            
            if (response && response.image) {
                const pageImage = document.getElementById('page-image');
                pageImage.src = response.image;
                scene.image = response.image;
            }
        } catch (error) {
            console.error('Failed to regenerate image:', error);
            this.showNotification('Failed to regenerate image', 'error');
        } finally {
            this.showImageLoading(false);
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    enablePDFDownload() {
        const exportBtn = document.getElementById('export-pdf');
        const shareBtn = document.getElementById('share-story');
        
        if (exportBtn) {
            exportBtn.classList.remove('hidden');
            exportBtn.addEventListener('click', () => this.downloadPDF());
        }
        
        if (shareBtn) {
            shareBtn.classList.remove('hidden');
            shareBtn.addEventListener('click', () => this.shareStory());
        }
    }

    async downloadPDF() {
        try {
            this.showNotification('Generating PDF...');
            const response = await window.api?.exportPDF(this.storyData.id);
            
            if (response && response.url) {
                // Download the PDF
                const link = document.createElement('a');
                link.href = response.url;
                link.download = `${this.storyData.title}.pdf`;
                link.click();
                
                this.showNotification('PDF downloaded!', 'success');
            }
        } catch (error) {
            console.error('Failed to generate PDF:', error);
            this.showNotification('Failed to generate PDF', 'error');
        }
    }

    async shareStory() {
        try {
            const shareData = {
                title: this.storyData.title,
                text: `Check out my story: ${this.storyData.title}`,
                url: window.location.href
            };
            
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback to clipboard
                await navigator.clipboard.writeText(window.location.href);
                this.showNotification('Link copied to clipboard!');
            }
        } catch (error) {
            console.error('Error sharing:', error);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#6366f1'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Add new scene to story after choice selection
    addSceneToStory(sceneData) {
        if (this.storyData && sceneData) {
            // Ensure scene has proper structure
            const scene = {
                scene_number: sceneData.scene_number || this.storyData.scenes.length + 1,
                title: sceneData.title,
                text: sceneData.text || sceneData.content,
                image_prompt: sceneData.image_prompt,
                characters_present: sceneData.characters_present || [],
                image_url: sceneData.image_url || null,
                scene_id: sceneData.scene_id || `scene_${Date.now()}`
            };
            
            this.storyData.scenes.push(scene);
            this.totalPages = this.storyData.scenes.length;
            
            // Update page indicator
            document.getElementById('total-pages').textContent = this.totalPages;
            
            console.log('Scene added. Total scenes:', this.totalPages);
        }
    }
}

// Initialize book viewer
window.bookViewer = new BookViewer();
document.addEventListener('DOMContentLoaded', () => {
    window.bookViewer.init();
});

// Add page flip animations
const style = document.createElement('style');
style.textContent = `
    @keyframes pageFlipOut {
        0% { transform: rotateY(0deg); opacity: 1; }
        100% { transform: rotateY(-90deg); opacity: 0; }
    }
    
    @keyframes pageFlipIn {
        0% { transform: rotateY(90deg); opacity: 0; }
        100% { transform: rotateY(0deg); opacity: 1; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
