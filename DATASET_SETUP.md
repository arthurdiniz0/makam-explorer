# Cairo Congress Dataset Setup Guide

This guide explains how to download and set up the Cairo Congress 1932 dataset for the Makam Explorer.

## **Required Dataset**

You need to download the **Cairo Congress of Arab Music (1932)** dataset, which contains:
- **333 audio recordings** (.mp3 files)
- **333 pitch analysis files** (.pickle files) 
- **Metadata CSV** with recording information
- **Histogram images** for visualization

## **Download the Dataset**

### **Official Dataset Sources**

1. **Analysis Data & Features** (Required):
   - **Zenodo Repository**: [Open Research Dataset of the 1932 Cairo Congress of Arab Music (ORD-CC32)](https://zenodo.org/records/15682346)
   - **File**: `CairoCong1932_features_plots_2025-06-17.zip` (355.7 MB)
   - **Contains**: Pickle files, CSV metadata, histogram plots, Python scripts

2. **Audio Recordings** (Required):
   - **Internet Archive**: [Cairo Congress Audio Collection](https://archive.org/details/13.PsaumeDeLaTristesse)
   - **Contains**: All 333 MP3 recordings from the 18 CDs

3. **Additional Metadata**:
   - **MusicBrainz**: [Release Information](https://musicbrainz.org/release/25d66aec-1463-4a0b-a331-d3bbe587e71c)

## **Expected Dataset Structure**

After downloading, you should have two main folders:
```
Downloads/
├── Audio_Files/  # From Internet Archive
│   ├── CD 1/
│   │   ├── 01. Les nuits damour.mp3
│   │   ├── 02. Mon amour ma quitté alors que je nai aucun tort.mp3
│   │   └── ... (more .mp3 files)
│   ├── CD 2/
│   └── ... (CD 3 through CD 18)
└── CairoCong1932_features_plots_2025-06-17/  # From Zenodo
    ├── allfiles_metadata.csv
    ├── CD 1/
    │   ├── 01. Les nuits damour.h.tonic.jpeg
    │   ├── 01. Les nuits damour.pickle
    │   └── ... (more .pickle and .jpeg files)
    ├── CD 2/
    └── ... (CD 3 through CD 18)
```

## **Setup Instructions**

### **1. Clone this Repository**
```bash
git clone https://github.com/your-username/makam-explorer.git
cd makam-explorer
```

### **2. Install Dependencies**
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies (for analysis scripts)
pip install -r requirements.txt
```

### **3. Set Up Dataset Directories**
```bash
# Create required directories
mkdir -p data/cairo-congress-1932-features
mkdir -p public/data/cairo-congress-1932/metadata
mkdir -p public/data/cairo-congress-1932/audio
mkdir -p public/data/cairo-congress-1932/analysis
mkdir -p public/data/cairo-congress-1932/histograms
```

### **4. Extract Downloaded Files**
```bash
# Extract the Zenodo dataset
unzip CairoCong1932_features_plots_2025-06-17.zip

# Extract audio files from Internet Archive download
# (File structure may vary depending on download method)
```

### **5. Copy Analysis Files**
```bash
# Copy the features folder for processing
cp -r CairoCong1932_features_plots_2025-06-17 data/cairo-congress-1932-features
```

### **6. Set Up Web-Accessible Metadata**
```bash
# Copy metadata for web app
cp data/cairo-congress-1932-features/allfiles_metadata.csv public/data/cairo-congress-1932/metadata/
cp data/cairo-congress-1932-features/mode_regions_count.csv public/data/cairo-congress-1932/metadata/
cp data/cairo-congress-1932-features/region_modes_count.csv public/data/cairo-congress-1932/metadata/

# Copy histogram images
cp -r data/cairo-congress-1932-features/tonic_aligned_hists/* public/data/cairo-congress-1932/histograms/
```

### **7. Convert Pitch Data**
```bash
# Convert .pickle files to .json for web app
cd analysis/scripts
python convert_pickles.py
cd ../..
```

### **8. Copy Audio Files for Web Access**
```bash
# Copy audio files to web directory (adjust path to your download location)
python3 -c "
import os
import shutil
from pathlib import Path

# Adjust this path to wherever you extracted the audio files
downloaded_audio_dir = Path('Downloaded_Audio_Folder')  # Change this to your download path
public_audio_dir = Path('public/data/cairo-congress-1932/audio')

for cd_dir in downloaded_audio_dir.glob('CD *'):
    cd_name = cd_dir.name
    target_dir = public_audio_dir / cd_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for mp3_file in cd_dir.glob('*.mp3'):
        target_file = target_dir / mp3_file.name
        if not target_file.exists():
            shutil.copy2(mp3_file, target_file)
            print(f'Copied: {mp3_file.name}')

print('Audio files copied successfully!')
"
```

### **9. Download Instrument Samples**
```bash
# Download piano/instrument samples for interactive playing
node scripts/download-samples.js
```

### **10. Start the Application**
```bash
npm start
```

The application should open at `http://localhost:3000`

## **Verification**

After setup, verify everything works:

1. **Check file counts**:
   ```bash
   find data/cairo-congress-1932-features -name "*.pickle" | wc -l                    # Should be 333
   find public/data/cairo-congress-1932/analysis -name "*.json" | wc -l              # Should be 333
   find public/data/cairo-congress-1932/audio -name "*.mp3" | wc -l                  # Should be 333
   find public/samples -name "*.mp3" | wc -l                                         # Should be 31
   ```

2. **Test the web application**:
   - Load different makam modes
   - Select various recordings
   - Verify audio playback works
   - Test piano key interaction
   - Check pitch visualization

## **Dataset Information**

- **Total Recordings**: 333 tracks across 18 CDs
- **Regions**: Egypt, Iraq, Syria, Tunisia, Morocco, Algeria
- **Makam Modes**: rast, bayati, hijaz, husayni, saba, and others
- **Time Period**: 1932 Cairo Congress of Arab Music
- **File Sizes**: ~3GB total (audio + analysis data)

## **Troubleshooting**

### **Missing Audio Files**
- Verify the dataset download is complete
- Check file paths match the expected structure
- Ensure files were copied to correct directories

### **Pitch Data Not Loading**
- Verify .pickle files were converted to .json
- Check `public/subsetRecordings/` contains .json files
- Run the conversion script again if needed

### **Piano Not Working**
- Ensure instrument samples were downloaded
- Check `public/samples/` contains flute and guitar folders
- Re-run `node scripts/download-samples.js`

### **Metadata Not Loading**
- Verify `public/data/metadata/allfiles_metadata.csv` exists
- Check CSV file format and encoding
- Ensure file paths in CSV match actual file structure

## **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all setup steps were completed
3. Check file permissions and paths
4. Open an issue on the GitHub repository

---

**Note**: The dataset is large (~3GB) and not included in this repository. You must download and set it up separately following this guide.
