/**
 * API Service Module
 */

class APIService {
    constructor() {
        this.baseURL = Config.API_URL;
        this.headers = {
            'Content-Type': 'application/json'
        };
    }
    
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.headers,
                    ...options.headers
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    // Story endpoints
    async generateStory(params) {
        return this.request(Config.endpoints.generateStory, {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
    
    async getStory(storyId) {
        return this.request(`${Config.endpoints.getStory}/${storyId}`);
    }
    
    async listStories() {
        return this.request(Config.endpoints.listStories);
    }
    
    async deleteStory(storyId) {
        return this.request(`${Config.endpoints.deleteStory}/${storyId}`, {
            method: 'DELETE'
        });
    }
    
    // Image endpoints
    async generateSceneImage(params) {
        return this.request(Config.endpoints.generateImage, {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
    
    async refineCharacter(params) {
        return this.request(Config.endpoints.refineCharacter, {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
    
    // Character endpoints
    async updateCharacter(params) {
        return this.request(Config.endpoints.updateCharacter, {
            method: 'PUT',
            body: JSON.stringify(params)
        });
    }
    
    // Export endpoints
    async exportPDF(storyId, images) {
        return this.request(Config.endpoints.exportPDF, {
            method: 'POST',
            body: JSON.stringify({ story_id: storyId, images })
        });
    }
    
    async exportHTML(storyId, images) {
        return this.request(Config.endpoints.exportHTML, {
            method: 'POST',
            body: JSON.stringify({ story_id: storyId, images })
        });
    }
    
    async exportJSON(storyId, images) {
        return this.request(Config.endpoints.exportJSON, {
            method: 'POST',
            body: JSON.stringify({ story_id: storyId, images })
        });
    }
    
    // Story choice endpoints
    async getStoryChoices(context) {
        return this.request('/api/story-choices', {
            method: 'POST',
            body: JSON.stringify(context)
        });
    }
    
    async generateSceneFromChoice(params) {
        return this.request('/api/generate-scene-from-choice', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }
    
    async regenerateImage(storyId, sceneIndex) {
        return this.request(Config.endpoints.generateImage, {
            method: 'POST',
            body: JSON.stringify({
                story_id: storyId,
                scene_number: sceneIndex + 1,
                regenerate: true
            })
        });
    }
    
    // System endpoints
    async checkHealth() {
        return this.request(Config.endpoints.health);
    }
    
    async getStatus() {
        return this.request(Config.endpoints.status);
    }
}