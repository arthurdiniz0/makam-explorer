#!/bin/bash

# Makam Explorer Setup Script
# This script helps set up the Cairo Congress dataset after downloading

set -e  # Exit on any error

echo "🎵 Makam Explorer - Dataset Setup Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the makam-explorer root directory"
    exit 1
fi

print_status "Setting up directory structure..."

# Create required directories
mkdir -p data/cairo-congress-1932-features
mkdir -p public/data/cairo-congress-1932/metadata
mkdir -p public/data/cairo-congress-1932/audio
mkdir -p public/data/cairo-congress-1932/analysis
mkdir -p public/data/cairo-congress-1932/histograms

print_success "Directory structure created"

# Check for dataset folders
AUDIO_FOLDER=""
FEATURES_FOLDER=""

print_status "Looking for downloaded dataset folders..."

# Look for audio folder
if [ -d "Congrès de musique arabe du Caire"* ]; then
    AUDIO_FOLDER=$(find . -maxdepth 1 -name "Congrès de musique arabe du Caire*" -type d | head -1)
    print_success "Found audio folder: $AUDIO_FOLDER"
elif [ -d "../Congrès de musique arabe du Caire"* ]; then
    AUDIO_FOLDER=$(find .. -maxdepth 1 -name "Congrès de musique arabe du Caire*" -type d | head -1)
    print_success "Found audio folder: $AUDIO_FOLDER"
else
    print_error "Audio folder not found!"
    print_warning "Please download the Cairo Congress audio dataset first."
    print_warning "See DATASET_SETUP.md for instructions."
    exit 1
fi

# Look for features folder
if [ -d "CairoCong1932_features_plots"* ]; then
    FEATURES_FOLDER=$(find . -maxdepth 1 -name "CairoCong1932_features_plots*" -type d | head -1)
    print_success "Found features folder: $FEATURES_FOLDER"
elif [ -d "../CairoCong1932_features_plots"* ]; then
    FEATURES_FOLDER=$(find .. -maxdepth 1 -name "CairoCong1932_features_plots*" -type d | head -1)
    print_success "Found features folder: $FEATURES_FOLDER"
else
    print_error "Features folder not found!"
    print_warning "Please download the Cairo Congress features dataset first."
    print_warning "See DATASET_SETUP.md for instructions."
    exit 1
fi

print_status "Audio files will be copied directly to web directory..."
# We'll copy directly to public directory below, no intermediate storage needed

print_status "Copying analysis files for processing..."
cp -r "$FEATURES_FOLDER" data/cairo-congress-1932-features
print_success "Analysis files copied"

print_status "Setting up web-accessible metadata..."
cp data/cairo-congress-1932-features/allfiles_metadata.csv public/data/cairo-congress-1932/metadata/
if [ -f data/cairo-congress-1932-features/mode_regions_count.csv ]; then
    cp data/cairo-congress-1932-features/mode_regions_count.csv public/data/cairo-congress-1932/metadata/
fi
if [ -f data/cairo-congress-1932-features/region_modes_count.csv ]; then
    cp data/cairo-congress-1932-features/region_modes_count.csv public/data/cairo-congress-1932/metadata/
fi
print_success "Metadata files copied"

print_status "Copying histogram images..."
if [ -d data/cairo-congress-1932-features/tonic_aligned_hists ]; then
    cp -r data/cairo-congress-1932-features/tonic_aligned_hists/* public/data/cairo-congress-1932/histograms/ 2>/dev/null || true
    print_success "Histogram images copied"
else
    print_warning "No histogram images found - this is optional"
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python not found! Please install Python 3.8+ to continue."
    exit 1
fi

print_status "Converting pitch data files (.pickle to .json)..."
cd analysis/scripts
$PYTHON_CMD convert_pickles.py
cd ../..
print_success "Pitch data converted"

print_status "Copying audio files directly to web directory..."
$PYTHON_CMD -c "
import os
import shutil
from pathlib import Path

# Use the downloaded audio folder directly
audio_folder = Path('$AUDIO_FOLDER')
public_audio_dir = Path('public/data/cairo-congress-1932/audio')

copied_count = 0
for cd_dir in audio_folder.glob('CD *'):
    cd_name = cd_dir.name
    target_dir = public_audio_dir / cd_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for mp3_file in cd_dir.glob('*.mp3'):
        target_file = target_dir / mp3_file.name
        if not target_file.exists():
            shutil.copy2(mp3_file, target_file)
            copied_count += 1

print(f'Copied {copied_count} audio files successfully!')
"
print_success "Audio files copied to web directory"

# Check if Node.js is available
if command -v node &> /dev/null; then
    print_status "Downloading instrument samples..."
    node scripts/download-samples.js
    print_success "Instrument samples downloaded"
else
    print_warning "Node.js not found - skipping instrument samples download"
    print_warning "Run 'node scripts/download-samples.js' manually after installing Node.js"
fi

print_status "Verifying setup..."

# Count files to verify
AUDIO_COUNT=$(find public/subsetRecordings -name "*.mp3" 2>/dev/null | wc -l | tr -d ' ')
JSON_COUNT=$(find public/subsetRecordings -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
SAMPLE_COUNT=$(find public/samples -name "*.mp3" 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "📊 Setup Verification:"
echo "   Audio files: $AUDIO_COUNT (expected: 333)"
echo "   JSON pitch files: $JSON_COUNT (expected: 333)"
echo "   Instrument samples: $SAMPLE_COUNT (expected: 31)"

if [ "$AUDIO_COUNT" -gt 300 ] && [ "$JSON_COUNT" -gt 300 ]; then
    print_success "Setup completed successfully!"
    echo ""
    echo "🚀 Ready to start!"
    echo "   Run: npm install"
    echo "   Then: npm start"
    echo ""
    echo "   The app will be available at: http://localhost:3000"
else
    print_warning "Setup completed with some issues"
    print_warning "Some files may be missing - check the counts above"
    print_warning "See DATASET_SETUP.md for troubleshooting"
fi

echo ""
print_status "Setup script completed!"