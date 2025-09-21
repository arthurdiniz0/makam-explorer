# 🎵 Makam Explorer

An interactive web application for exploring and visualizing Makam music recordings from the historic **1932 Cairo Congress of Arab Music**. This tool provides real-time pitch visualization, interactive piano display, and comprehensive analysis of traditional Arab music modes.

![Makam Explorer Demo](https://img.shields.io/badge/Demo-Live-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue) ![React](https://img.shields.io/badge/React-18.0-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green)

## Features

### **Interactive Music Analysis**
- **Real-time pitch visualization** with piano roll display
- **Interactive piano keyboard** with playable keys (mouse and keyboard input)
- **Multiple pitch detection methods** (pYIN, CREPE, Makam-specific)
- **Pitch histogram analysis** showing note distribution patterns
- **Adjustable playback speed** for detailed analysis

### **Historic 1932 Cairo Congress Dataset**
- **333 historic recordings** across 18 CDs
- **Multiple makam modes**: rast, bayati, hijaz, husayni, saba, and more
- **Comprehensive metadata** with artists, regions, and performance details
- **Tonic-aligned histograms** for accurate cross-regional comparison

## **Quick Start**

### **Prerequisites**
- Node.js 14+ and npm 6+
- Python 3.8+ (for data processing)
- ~3GB free space for dataset

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/makam-explorer.git
cd makam-explorer
```

### **2. Install Dependencies**
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### **3. Download Dataset** 
**Important**: The dataset is NOT included in this repository due to size (~3GB)

**Download from official sources:**

1. **Analysis Data**: [Zenodo - ORD-CC32 Dataset](https://zenodo.org/records/15682346) (355.7 MB)
2. **Audio Files**: [Internet Archive - Cairo Congress Audio](https://archive.org/details/13.PsaumeDeLaTristesse) (~2.5 GB)

See **[DATASET_SETUP.md](DATASET_SETUP.md)** for detailed download and setup instructions.

**Quick summary:**
1. Download both the Zenodo analysis data and Internet Archive audio
2. Extract files to your local machine
3. Run the setup script to organize the data
4. Convert analysis files to web format

### **4. Run Setup Script**
```bash
# After downloading the dataset, run:
chmod +x setup.sh
./setup.sh
```

### **5. Start Application**
```bash
npm start
```

Visit `http://localhost:3000` to explore the Makam recordings!

## **Project Structure**

```
makam-explorer/
├── src/                             # React application source
├── public/                          # Web-accessible files
│   ├── data/cairo-congress-1932/    # Cairo Congress dataset
│   │   ├── metadata/               # Recording metadata (CSV)
│   │   ├── audio/                  # Audio recordings by CD
│   │   ├── analysis/               # Pitch data (JSON) by CD
│   │   └── histograms/             # Pitch analysis visualizations
│   └── samples/                    # Instrument samples (auto-downloaded)
├── data/                           # Raw analysis dataset (not in git)
│   └── cairo-congress-1932-features/  # Original pickle files for processing
├── analysis/scripts/               # Data processing tools
├── scripts/                        # Utility scripts
├── DATASET_SETUP.md               # Dataset download guide
└── requirements.txt               # Python dependencies
```

## **Usage Guide**

### **Basic Exploration**
1. **Select a makam mode** from the dropdown (e.g., "rast", "bayati")
2. **Choose a recording** from the filtered list
3. **Play audio** and watch real-time pitch visualization
4. **Click piano keys** to hear the makam intervals
5. **Switch pitch methods** to compare analysis algorithms

### **Features**
- **Keyboard shortcuts**: Use QWERTY keys to play piano
- **Speed control**: Adjust playback speed for detailed analysis
- **Instrument switching**: Toggle between flute and guitar sounds
- **Makam information**: Click "About Makam" for theoretical details
- **Regional comparison**: Compare the same makam across different regions

##**License & Citation**

This project is licensed under the **MIT License**.