/**
 * Component Loader - Loads HTML components dynamically
 */

class ComponentLoader {
    constructor() {
        this.components = [
            'html/components/setup-screen.html',
            'html/components/book-viewer.html',
            'html/components/loading-overlay.html',
            'html/components/error-modal.html',
            'html/components/swipe-hint.html'
        ];
    }

    async loadComponent(path) {
        try {
            const response = await fetch(path);
            if (!response.ok) {
                throw new Error(`Failed to load component: ${path}`);
            }
            return await response.text();
        } catch (error) {
            console.error(`Error loading component ${path}:`, error);
            return '';
        }
    }

    async loadAllComponents() {
        const app = document.getElementById('app');
        if (!app) {
            console.error('App container not found');
            return;
        }

        // Load all components
        const componentPromises = this.components.map(path => this.loadComponent(path));
        const componentHTML = await Promise.all(componentPromises);
        
        // Inject all components into the app
        app.innerHTML = componentHTML.join('');
        
        // Dispatch event when all components are loaded
        window.dispatchEvent(new Event('componentsLoaded'));
    }

    async init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.loadAllComponents());
        } else {
            await this.loadAllComponents();
        }
    }
}

// Initialize component loader
const componentLoader = new ComponentLoader();
componentLoader.init();