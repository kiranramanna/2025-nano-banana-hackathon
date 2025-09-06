/**
 * Configuration module
 */

const Config = {
    API_URL: '/api',  // Now using relative path since served from same server
    IMAGE_BASE_URL: '',  // Same origin, no need for full URL
    
    // Default values
    defaults: {
        ageGroup: '7-10',
        genre: 'adventure',
        numScenes: 5,
        artStyle: 'watercolor',
        aspectRatio: '16:9'
    },
    
    // Validation rules
    validation: {
        minPromptLength: 10,
        minScenes: 3,
        maxScenes: 10,
        maxCharacters: 5
    },
    
    // UI settings
    ui: {
        loadingDelay: 500,
        animationDuration: 300,
        autoSaveInterval: 30000, // 30 seconds
        maxStorageItems: 10
    },
    
    // API endpoints
    endpoints: {
        generateStory: '/generate-story',
        getStory: '/get-story',
        listStories: '/stories',
        generateImage: '/generate-scene-image',
        refineCharacter: '/refine-character',
        updateCharacter: '/update-character',
        deleteStory: '/delete-story',
        exportPDF: '/export/pdf',
        exportHTML: '/export/html',
        exportJSON: '/export/json',
        health: '/health',
        status: '/status'
    }
};

// Freeze config to prevent modifications
Object.freeze(Config);
Object.freeze(Config.defaults);
Object.freeze(Config.validation);
Object.freeze(Config.ui);
Object.freeze(Config.endpoints);