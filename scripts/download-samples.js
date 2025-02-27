const fs = require('fs');
const path = require('path');
const https = require('https');

// Update the base URL to point to the tonejs-instruments repository
const BASE_URL = 'https://raw.githubusercontent.com/nbrosowsky/tonejs-instruments/master/samples';
const SAMPLES_DIR = path.join(process.cwd(), 'public', 'samples');

const INSTRUMENTS = {
    'flute': [
        'A4', 'A5', 'A6',
        'C4', 'C5', 'C6', 'C7',
        'E4', 'E5', 'E6'
    ],
    'guitar-acoustic': [
        'A2', 'A3', 'A4',
        'B2', 'B3', 'B4',
        'C3', 'C4', 'C5',
        'D2', 'D3', 'D4',
        'E2', 'E3', 'E4',
        'F2', 'F3', 'F4',
        'G2', 'G3', 'G4'
    ]
};

async function downloadFile(url, destPath) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(destPath);
        https.get(url, (response) => {
            if (response.statusCode === 200) {
                response.pipe(file);
                file.on('finish', () => {
                    file.close();
                    resolve();
                });
            } else {
                fs.unlink(destPath, () => {});
                reject(new Error(`HTTP Status ${response.statusCode}`));
            }
        }).on('error', (err) => {
            fs.unlink(destPath, () => {});
            reject(err);
        });
    });
}

async function downloadInstrument(instrument) {
    const instrumentDir = path.join(SAMPLES_DIR, instrument);
    
    // Create instrument directory if it doesn't exist
    if (!fs.existsSync(instrumentDir)) {
        fs.mkdirSync(instrumentDir, { recursive: true });
        console.log(`Created directory for ${instrument}`);
    }

    console.log(`Downloading ${instrument} samples...`);
    
    for (const note of INSTRUMENTS[instrument]) {
        const fileName = `${note}.mp3`;
        const url = `${BASE_URL}/${instrument}/${fileName}`;
        const destPath = path.join(instrumentDir, fileName);
        
        console.log(`Downloading ${fileName} from ${url}...`);
        try {
            await downloadFile(url, destPath);
            console.log(`Successfully downloaded ${fileName}`);
        } catch (error) {
            console.error(`Failed to download ${fileName}:`, error);
        }
    }
}

async function main() {
    // Create samples directory if it doesn't exist
    if (!fs.existsSync(SAMPLES_DIR)) {
        fs.mkdirSync(SAMPLES_DIR, { recursive: true });
        console.log('Created samples directory:', SAMPLES_DIR);
    }

    // Download all instruments
    for (const instrument of Object.keys(INSTRUMENTS)) {
        await downloadInstrument(instrument);
    }
}

main().catch(console.error); 