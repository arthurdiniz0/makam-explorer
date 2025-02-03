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

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Usage

1. Select a Makam from the dropdown menu
2. Choose a recording to analyze
3. Use the audio controls to play/pause and adjust playback speed
4. Select different pitch detection methods to compare analyses
5. Click the "About Makam" button to learn more about the selected Makam
6. Interact with the piano visualization using mouse or keyboard

## Data Processing

The application uses preprocessed pitch data from audio recordings. To process new recordings:

1. Place audio files in the `public/subsetRecordings` directory
2. Run the conversion script:
```bash
python convert_pickles.py
```

## Technologies Used

- React.js
- D3.js for data visualization
- Web Audio API for sound synthesis
- Python for data processing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MakamWorld for providing Makam reference information
- Original audio recordings and their performers
- Research papers and tools for pitch detection algorithms
