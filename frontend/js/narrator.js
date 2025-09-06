/**
 * Narration Service Module
 */

class NarrationService {
    constructor() {
        this.synth = window.speechSynthesis;
        this.currentUtterance = null;
        this.isSupported = 'speechSynthesis' in window;
        this.voices = [];
        this.selectedVoice = null;
        
        if (this.isSupported) {
            this.loadVoices();
        }
    }
    
    loadVoices() {
        this.voices = this.synth.getVoices();
        
        // Chrome loads voices asynchronously
        if (this.voices.length === 0) {
            this.synth.addEventListener('voiceschanged', () => {
                this.voices = this.synth.getVoices();
                this.selectDefaultVoice();
            });
        } else {
            this.selectDefaultVoice();
        }
    }
    
    selectDefaultVoice() {
        // Try to find a child-friendly voice
        const preferredVoices = [
            'Google UK English Female',
            'Google US English',
            'Microsoft Zira',
            'Samantha',
            'Victoria'
        ];
        
        for (const voiceName of preferredVoices) {
            const voice = this.voices.find(v => v.name.includes(voiceName));
            if (voice) {
                this.selectedVoice = voice;
                break;
            }
        }
        
        // Fallback to first available voice
        if (!this.selectedVoice && this.voices.length > 0) {
            this.selectedVoice = this.voices[0];
        }
    }
    
    narrate(text, options = {}) {
        if (!this.isSupported) {
            console.warn('Text-to-speech not supported');
            return Promise.reject('Text-to-speech not supported');
        }
        
        // Stop any ongoing narration
        this.stop();
        
        return new Promise((resolve, reject) => {
            this.currentUtterance = new SpeechSynthesisUtterance(text);
            
            // Apply options
            this.currentUtterance.rate = options.rate || 0.9;
            this.currentUtterance.pitch = options.pitch || 1.1;
            this.currentUtterance.volume = options.volume || 1.0;
            
            if (this.selectedVoice) {
                this.currentUtterance.voice = this.selectedVoice;
            }
            
            // Event handlers
            this.currentUtterance.onend = () => {
                this.currentUtterance = null;
                resolve();
            };
            
            this.currentUtterance.onerror = (event) => {
                this.currentUtterance = null;
                reject(event.error);
            };
            
            // Start speaking
            this.synth.speak(this.currentUtterance);
        });
    }
    
    pause() {
        if (this.synth.speaking && !this.synth.paused) {
            this.synth.pause();
            return true;
        }
        return false;
    }
    
    resume() {
        if (this.synth.paused) {
            this.synth.resume();
            return true;
        }
        return false;
    }
    
    stop() {
        if (this.synth.speaking) {
            this.synth.cancel();
            this.currentUtterance = null;
            return true;
        }
        return false;
    }
    
    isSpeaking() {
        return this.synth.speaking;
    }
    
    isPaused() {
        return this.synth.paused;
    }
    
    getVoices() {
        return this.voices;
    }
    
    setVoice(voiceIndex) {
        if (voiceIndex >= 0 && voiceIndex < this.voices.length) {
            this.selectedVoice = this.voices[voiceIndex];
            return true;
        }
        return false;
    }
    
    // Scene narration with emphasis
    narrateScene(scene, options = {}) {
        // Add pauses and emphasis for better storytelling
        let text = scene.title + '. ';
        text += scene.text;
        
        // Replace some punctuation for better pacing
        text = text.replace(/\.\.\./g, '...,');
        text = text.replace(/!/g, '!,');
        text = text.replace(/\?/g, '?,');
        
        return this.narrate(text, {
            rate: 0.85,  // Slightly slower for story
            pitch: 1.1,  // Slightly higher for child-friendly
            ...options
        });
    }
    
    // Character dialogue with different voices
    narrateDialogue(character, dialogue, options = {}) {
        // Adjust pitch based on character type
        const pitchMap = {
            'child': 1.3,
            'adult': 1.0,
            'elderly': 0.9,
            'robot': 0.8,
            'animal': 1.2
        };
        
        const characterType = this.detectCharacterType(character);
        const pitch = pitchMap[characterType] || 1.0;
        
        return this.narrate(dialogue, {
            rate: 0.9,
            pitch,
            ...options
        });
    }
    
    detectCharacterType(character) {
        const lowerDesc = character.description.toLowerCase();
        
        if (lowerDesc.includes('child') || lowerDesc.includes('young')) {
            return 'child';
        } else if (lowerDesc.includes('old') || lowerDesc.includes('elderly')) {
            return 'elderly';
        } else if (lowerDesc.includes('robot') || lowerDesc.includes('android')) {
            return 'robot';
        } else if (lowerDesc.includes('animal') || lowerDesc.includes('creature')) {
            return 'animal';
        }
        
        return 'adult';
    }
}