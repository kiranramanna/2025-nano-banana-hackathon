/**
 * Local Storage Service Module
 */

class StorageService {
    constructor() {
        this.prefix = 'storybook_';
        this.maxItems = Config.ui.maxStorageItems;
    }
    
    // Story management
    saveStory(story, images = {}) {
        const key = `${this.prefix}story_${story.story_id || story.id}`;
        const data = {
            story,
            images,
            timestamp: new Date().toISOString()
        };
        
        try {
            localStorage.setItem(key, JSON.stringify(data));
            this.enforceStorageLimit();
            return true;
        } catch (e) {
            console.error('Failed to save story:', e);
            return false;
        }
    }
    
    getStory(storyId) {
        const key = `${this.prefix}story_${storyId}`;
        
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.error('Failed to load story:', e);
            return null;
        }
    }
    
    getAllStories() {
        const stories = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            
            if (key && key.startsWith(`${this.prefix}story_`)) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    stories.push(data);
                } catch (e) {
                    console.error('Failed to parse story:', e);
                }
            }
        }
        
        // Sort by timestamp (newest first)
        stories.sort((a, b) => {
            const dateA = new Date(a.timestamp || 0);
            const dateB = new Date(b.timestamp || 0);
            return dateB - dateA;
        });
        
        return stories;
    }
    
    deleteStory(storyId) {
        const key = `${this.prefix}story_${storyId}`;
        
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Failed to delete story:', e);
            return false;
        }
    }
    
    // Settings management
    saveSetting(name, value) {
        const key = `${this.prefix}setting_${name}`;
        
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Failed to save setting:', e);
            return false;
        }
    }
    
    getSetting(name, defaultValue = null) {
        const key = `${this.prefix}setting_${name}`;
        
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (e) {
            console.error('Failed to load setting:', e);
            return defaultValue;
        }
    }
    
    // Preferences
    savePreferences(preferences) {
        return this.saveSetting('preferences', preferences);
    }
    
    getPreferences() {
        return this.getSetting('preferences', {
            ageGroup: Config.defaults.ageGroup,
            genre: Config.defaults.genre,
            artStyle: Config.defaults.artStyle,
            autoSave: true,
            narrationEnabled: true
        });
    }
    
    // Cache management
    enforceStorageLimit() {
        const stories = this.getAllStories();
        
        if (stories.length > this.maxItems) {
            // Remove oldest stories
            const toRemove = stories.slice(this.maxItems);
            
            toRemove.forEach(item => {
                const storyId = item.story?.story_id || item.story?.id;
                if (storyId) {
                    this.deleteStory(storyId);
                }
            });
        }
    }
    
    clearAllStories() {
        const keysToRemove = [];
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(`${this.prefix}story_`)) {
                keysToRemove.push(key);
            }
        }
        
        keysToRemove.forEach(key => localStorage.removeItem(key));
    }
    
    getStorageSize() {
        let size = 0;
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(this.prefix)) {
                const value = localStorage.getItem(key);
                size += key.length + (value ? value.length : 0);
            }
        }
        
        return size;
    }
    
    // Export/Import
    exportData() {
        const data = {
            stories: this.getAllStories(),
            preferences: this.getPreferences(),
            exportDate: new Date().toISOString()
        };
        
        return JSON.stringify(data, null, 2);
    }
    
    importData(jsonData) {
        try {
            const data = JSON.parse(jsonData);
            
            // Import stories
            if (data.stories && Array.isArray(data.stories)) {
                data.stories.forEach(item => {
                    if (item.story) {
                        this.saveStory(item.story, item.images);
                    }
                });
            }
            
            // Import preferences
            if (data.preferences) {
                this.savePreferences(data.preferences);
            }
            
            return true;
        } catch (e) {
            console.error('Failed to import data:', e);
            return false;
        }
    }
}