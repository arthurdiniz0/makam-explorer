# Makam Explorer

An interactive web application for exploring and visualizing Makam music recordings. This tool provides real-time pitch visualization, interactive piano display, and pitch histogram analysis for understanding the melodic characteristics of Makam music.

## Features

- Real-time pitch visualization with piano roll display
- Interactive piano keyboard with playable keys (mouse and keyboard input)
- Pitch histogram analysis showing note distribution
- Multiple pitch detection methods (pYIN, CREPE, Makam-specific)
- Adjustable playback speed
- Detailed Makam information modal
- Support for multiple recordings and Makam modes

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)
- Python 3.7+ (for data processing scripts)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/makam-explorer.git
cd makam-explorer
```

2. Install dependencies:
```bash
npm install
```

3. Download required data files:
   
   a. **Audio recordings** from Archive.org:
      - Visit [https://archive.org/details/13.PsaumeDeLaTristesse](https://archive.org/details/13.PsaumeDeLaTristesse)
      - Download the VBR MP3 compressed file: [Direct Link](https://archive.org/compress/13.PsaumeDeLaTristesse/formats=VBR%20MP3&file=/13.PsaumeDeLaTristesse.zip)
      - Extract the downloaded ZIP file
      - Move all MP3 files to the `public/subsetRecordings` directory:
      ```bash
      # Create directory if it doesn't exist
      mkdir -p public/subsetRecordings
      
      # Move downloaded MP3 files to the correct location
      # Replace [DOWNLOAD_PATH] with your download location
      mv [DOWNLOAD_PATH]/*.mp3 public/subsetRecordings/
      ```

   b. **Pitch data files** from Zenodo:
      - Visit the Zenodo repository (link will be provided later)
      - Download the pickle files collection
      - Extract the downloaded files to a temporary directory
      - Process these files using the conversion script:
      ```bash
      # Process pickle files to generate JSON data
      python convert_pickles.py --input_dir [PATH_TO_EXTRACTED_PICKLES] --output_dir public/pitch_data
      ```

4. Verify data installation:
```bash
# Check if data files exist in correct locations
python check_json.py
```

5. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Complete Setup Script

For convenience, here's a shell script that automates the setup process after you've downloaded the required files:

```bash
#!/bin/bash

# Create required directories
mkdir -p public/subsetRecordings
mkdir -p public/pitch_data

# Check for downloads and prompt if they don't exist
if [ -z "$(ls -A [DOWNLOAD_PATH]/mp3)" ]; then
  echo "MP3 files not found!"
  echo "Please download from: https://archive.org/compress/13.PsaumeDeLaTristesse/formats=VBR%20MP3"
  exit 1
fi

if [ -z "$(ls -A [DOWNLOAD_PATH]/pickles)" ]; then
  echo "Pickle files not found!"
  echo "Please download from: [ZENODO_LINK]"
  exit 1
fi

# Copy MP3 files to the correct location
cp [DOWNLOAD_PATH]/mp3/*.mp3 public/subsetRecordings/

# Process pickle files
python convert_pickles.py --input_dir [DOWNLOAD_PATH]/pickles --output_dir public/pitch_data

# Verify installation
python check_json.py

echo "Setup complete! Run 'npm start' to launch the application."
```

Save this as `setup.sh` in the project root directory and run it after downloading the required files.

## Usage

1. Select a Makam from the dropdown menu
2. Choose a recording to analyze
3. Use the audio controls to play/pause and adjust playback speed
4. Select different pitch detection methods to compare analyses
5. Click the "About Makam" button to learn more about the selected Makam
6. Interact with the piano visualization using mouse or keyboard

## Data Processing

The application uses preprocessed pitch data from audio recordings. To process new or additional recordings:

1. Place audio files in the `public/subsetRecordings` directory
2. If you have new pickle files with pitch data, run the conversion script:
```bash
python convert_pickles.py --input_dir [PATH_TO_PICKLES] --output_dir public/pitch_data
```

## Common Issues and Troubleshooting

- **Missing audio files**: Ensure all MP3 files are properly placed in `public/subsetRecordings`
- **Missing pitch data**: Verify that the pickle conversion was successful and that JSON files exist in `public/pitch_data`
- **Playback issues**: Check browser console for errors. Some browsers may have restrictions on AudioContext initialization

## Technologies Used

- React.js
- D3.js for data visualization
- Web Audio API for sound synthesis
- Python for data processing
- Tone.js for audio synthesis and sample management

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MakamWorld for providing Makam reference information
- Original audio recordings and their performers
- Research papers and tools for pitch detection algorithms
- Internet Archive for hosting the audio recordings
