import * as Tone from 'tone';

const INSTRUMENTS = {
    'flute': {
        baseFreqs: {
            'A4': 440,    // A4 = 440 Hz
            'A5': 880,    // A5 = 880 Hz
            'A6': 1760,   // A6 = 1760 Hz
            'C4': 261.63, // C4 = 261.63 Hz
            'C5': 523.25, // C5 = 523.25 Hz
            'C6': 1046.50,// C6 = 1046.50 Hz
            'C7': 2093,   // C7 = 2093 Hz
            'E4': 329.63, // E4 = 329.63 Hz
            'E5': 659.26, // E5 = 659.26 Hz
            'E6': 1318.51 // E6 = 1318.51 Hz
        },
        sampleOffset: 0.2,
        volume: -5
    },
    'guitar-acoustic': {
        baseFreqs: {
            'A2': 110,     // A2 = 110 Hz
            'A3': 220,     // A3 = 220 Hz
            'A4': 440,     // A4 = 440 Hz
            'B2': 123.47,  // B2
            'B3': 246.94,  // B3
            'B4': 493.88,  // B4
            'C3': 130.81,  // C3
            'C4': 261.63,  // C4
            'C5': 523.25,  // C5
            'D2': 73.42,   // D2
            'D3': 146.83,  // D3
            'D4': 293.66,  // D4
            'E2': 82.41,   // E2
            'E3': 164.81,  // E3
            'E4': 329.63,  // E4
            'F2': 87.31,   // F2
            'F3': 174.61,  // F3
            'F4': 349.23,  // F4
            'G2': 98.00,   // G2
            'G3': 196.00,  // G3
            'G4': 392.00   // G4
        },
        sampleOffset: 0.1,
        volume: -8
    }
};

class InstrumentManager {
    constructor() {
        this.isStarted = false;
        this.playerPools = new Map();  // Map to store pools of players for each note
        this.isLoading = false;
        this.isReady = false;
        this.currentInstrument = 'flute';  // Default instrument
        this.baseUrl = '/samples/flute/';
        this.maxPolyphony = 4;  // Maximum number of simultaneous voices per note
        
        // Audio parameters
        this.rampTime = 0.015;  // 15ms ramp for volume changes
        
        // Keep track of active notes
        this.activeNotes = new Map();
        
        // Initialize reverb but don't connect it yet
        this.reverb = null;
        
        // Load instrument immediately
        this.loadInstrument().catch(err => {
            console.error('Failed to load instrument during initialization:', err);
        });
    }

    // Get current instrument configuration
    get instrumentConfig() {
        return INSTRUMENTS[this.currentInstrument];
    }

    // Change instrument
    async changeInstrument(instrumentName) {
        if (!INSTRUMENTS[instrumentName]) {
            throw new Error(`Invalid instrument: ${instrumentName}`);
        }
        if (instrumentName === this.currentInstrument && this.isReady) {
            return; // Already using this instrument
        }

        // Stop all currently playing notes
        for (const [frequency] of this.activeNotes) {
            await this.stopNote(frequency);
        }

        // Dispose current instrument
        this.dispose();

        // Set new instrument
        this.currentInstrument = instrumentName;
        
        // Load new instrument
        await this.loadInstrument();
    }

    async start() {
        if (!this.isStarted) {
            try {
                await Tone.start();
                this.isStarted = true;
                console.log('Tone.js started successfully');
            } catch (error) {
                console.error('Failed to start Tone.js:', error);
                throw error;
            }
        }
    }

    findClosestSample(targetFreq) {
        let closestNote = null;
        let minRatio = Infinity;
        
        for (const [note, baseFreq] of Object.entries(this.instrumentConfig.baseFreqs)) {
            // Calculate how much we'd need to pitch shift this sample
            const ratio = Math.abs(Math.log2(targetFreq / baseFreq));
            if (ratio < minRatio) {
                minRatio = ratio;
                closestNote = note;
            }
        }
        
        return {
            note: closestNote,
            baseFreq: this.instrumentConfig.baseFreqs[closestNote],
            playbackRate: targetFreq / this.instrumentConfig.baseFreqs[closestNote]
        };
    }

    async loadInstrument() {
        if (this.isLoading) {
            console.log('Instrument already loading...');
            return;
        }
        if (this.isReady) {
            console.log('Instrument already loaded');
            return;
        }

        this.isLoading = true;

        try {
            console.log(`Loading ${this.currentInstrument} samples...`);
            
            // Initialize and connect reverb first
            this.reverb = new Tone.Reverb({
                decay: 2,
                wet: 0.2
            }).toDestination();
            
            // Wait for reverb to initialize
            await this.reverb.generate();
            console.log('Reverb initialized');
            
            // Load each sample into multiple players for polyphony
            const loadPromises = Object.entries(this.instrumentConfig.baseFreqs).map(async ([note]) => {
                const players = [];
                for (let i = 0; i < this.maxPolyphony; i++) {
                    const volume = new Tone.Volume(this.instrumentConfig.volume).connect(this.reverb);
                    const player = new Tone.Player({
                        url: `/samples/${this.currentInstrument}/${note}.mp3`,
                        onload: () => {
                            console.log(`Loaded ${note} sample instance ${i + 1}`);
                        }
                    }).connect(volume);
                    
                    players.push({
                        player,
                        volume,
                        isActive: false
                    });
                }
                this.playerPools.set(note, players);
                // Wait for all players of this note to load
                return Promise.all(players.map(p => p.player.loaded));
            });

            // Wait for all samples to load
            await Promise.all(loadPromises);
            
            console.log(`All ${this.currentInstrument} samples loaded successfully`);
            this.isReady = true;
            this.isLoading = false;

        } catch (error) {
            console.error('Error loading samples:', error);
            this.isLoading = false;
            throw error;
        }
    }

    async ensureReady() {
        if (!this.isReady && !this.isLoading) {
            await this.loadInstrument();
        }
        
        // Wait for loading to complete if in progress
        if (this.isLoading) {
            await new Promise((resolve, reject) => {
                const checkInterval = setInterval(() => {
                    if (this.isReady) {
                        clearInterval(checkInterval);
                        resolve();
                    }
                    if (!this.isLoading && !this.isReady) {
                        clearInterval(checkInterval);
                        reject(new Error('Failed to load instrument'));
                    }
                }, 100);
            });
        }
    }

    // Get an available player from the pool
    getAvailablePlayer(note) {
        const pool = this.playerPools.get(note);
        if (!pool) return null;

        // First try to find an inactive player
        let playerInfo = pool.find(p => !p.isActive);
        if (!playerInfo) {
            // If all players are active, reuse the oldest one
            playerInfo = pool[0];
            // Gracefully stop the current playback
            this.stopPlayerGracefully(playerInfo);
        }
        return playerInfo;
    }

    async stopPlayerGracefully(playerInfo) {
        const { player, volume } = playerInfo;
        // Ramp volume down
        volume.volume.rampTo(-Infinity, this.rampTime);
        // Stop after the ramp
        setTimeout(() => {
            player.stop();
            volume.volume.value = this.instrumentConfig.volume;
            playerInfo.isActive = false;
        }, this.rampTime * 1000);
    }

    async playNote(frequency) {
        if (!this.isStarted) {
            await this.start();
        }

        try {
            await this.ensureReady();
            
            // Find the closest sample and calculate the playback rate
            const { note, playbackRate } = this.findClosestSample(frequency);
            
            // Get an available player for this note
            const playerInfo = this.getAvailablePlayer(note);
            if (!playerInfo) {
                console.error(`No player found for note ${note}`);
                return;
            }

            const { player, volume } = playerInfo;
            
            // Set up the player
            player.playbackRate = playbackRate;
            player.loop = true;
            
            // Start playing from the offset
            if (player.loaded) {
                // Start with volume at minimum
                volume.volume.value = -Infinity;
                player.start(undefined, this.instrumentConfig.sampleOffset);
                // Ramp up the volume
                volume.volume.rampTo(this.instrumentConfig.volume, this.rampTime);
                playerInfo.isActive = true;
                
                // Store the active note information
                const noteId = `${frequency}`;
                this.activeNotes.set(noteId, { playerInfo, note, playbackRate });
            } else {
                console.error('Player not loaded yet');
            }
            
        } catch (error) {
            console.error('Error playing note:', error);
        }
    }

    async stopNote(frequency) {
        if (!this.isReady) {
            console.error('No instrument loaded');
            return;
        }

        try {
            const noteId = `${frequency}`;
            if (this.activeNotes.has(noteId)) {
                const { playerInfo } = this.activeNotes.get(noteId);
                await this.stopPlayerGracefully(playerInfo);
                this.activeNotes.delete(noteId);
            }
        } catch (error) {
            console.error('Error stopping note:', error);
        }
    }

    dispose() {
        try {
            // Stop and dispose all players
            for (const players of this.playerPools.values()) {
                for (const { player, volume } of players) {
                    player.stop();
                    player.dispose();
                    volume.dispose();
                }
            }
            this.playerPools.clear();
            this.activeNotes.clear();

            // Dispose of reverb
            if (this.reverb) {
                this.reverb.dispose();
                this.reverb = null;
            }

            this.isReady = false;
            console.log('Instrument disposed');
        } catch (error) {
            console.error('Error disposing instrument:', error);
        }
    }
}

// Create a singleton instance
const instrumentManager = new InstrumentManager();
export default instrumentManager; 