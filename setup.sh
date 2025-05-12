#!/bin/bash

# Makam Explorer Setup Script
# This script automates the setup of the Makam Explorer application.

echo "=== Makam Explorer Setup ==="
echo "This script will help you set up the required data files for Makam Explorer."

# Check if required commands exist
command -v npm >/dev/null 2>&1 || { echo "Error: npm is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required but not installed."; exit 1; }

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing npm dependencies..."
  npm install
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install npm dependencies."
    exit 1
  fi
  echo "npm dependencies installed successfully."
fi

# Create required directories
mkdir -p public/subsetRecordings
mkdir -p public/pitch_data
mkdir -p public/samples

# Define download paths
MP3_DOWNLOAD_PATH="$HOME/Downloads/13.PsaumeDeLaTristesse"
PICKLE_DOWNLOAD_PATH="$HOME/Downloads/makam_pickles"

# Check for MP3 files
echo -n "Have you downloaded the MP3 files from Archive.org? (y/n): "
read mp3_downloaded

if [ "$mp3_downloaded" != "y" ]; then
  echo "Please download MP3 files from:"
  echo "https://archive.org/compress/13.PsaumeDeLaTristesse/formats=VBR%20MP3&file=/13.PsaumeDeLaTristesse.zip"
  echo "Extract the files and then run this script again."
  exit 1
fi

# Ask for MP3 location
echo -n "Enter the path to the MP3 files [$MP3_DOWNLOAD_PATH]: "
read mp3_path
mp3_path=${mp3_path:-$MP3_DOWNLOAD_PATH}

if [ ! -d "$mp3_path" ]; then
  echo "Error: Directory $mp3_path does not exist."
  exit 1
fi

MP3_COUNT=$(find "$mp3_path" -name "*.mp3" | wc -l)
if [ $MP3_COUNT -eq 0 ]; then
  echo "Error: No MP3 files found in $mp3_path."
  echo "Please download the MP3 files and extract them."
  exit 1
fi

echo "Found $MP3_COUNT MP3 files in $mp3_path."

# Check for pickle files
echo -n "Have you downloaded the pickle files from Zenodo? (y/n): "
read pickle_downloaded

if [ "$pickle_downloaded" != "y" ]; then
  echo "Please download pickle files from the Zenodo repository."
  echo "The link will be provided separately."
  echo "Extract the files and then run this script again."
  exit 1
fi

# Ask for pickle location
echo -n "Enter the path to the pickle files [$PICKLE_DOWNLOAD_PATH]: "
read pickle_path
pickle_path=${pickle_path:-$PICKLE_DOWNLOAD_PATH}

if [ ! -d "$pickle_path" ]; then
  echo "Error: Directory $pickle_path does not exist."
  exit 1
fi

PICKLE_COUNT=$(find "$pickle_path" -name "*.pickle" | wc -l)
if [ $PICKLE_COUNT -eq 0 ]; then
  echo "Error: No pickle files found in $pickle_path."
  echo "Please download the pickle files and extract them."
  exit 1
fi

echo "Found $PICKLE_COUNT pickle files in $pickle_path."

# Copy MP3 files
echo "Copying MP3 files to public/subsetRecordings..."
cp -r "$mp3_path"/*.mp3 public/subsetRecordings/
if [ $? -ne 0 ]; then
  echo "Error: Failed to copy MP3 files."
  exit 1
fi

# Process pickle files
echo "Processing pickle files..."
python3 convert_pickles.py --input_dir "$pickle_path" --output_dir public/pitch_data
if [ $? -ne 0 ]; then
  echo "Error: Failed to process pickle files."
  exit 1
fi

# Verify installation
echo "Verifying installation..."
python3 check_json.py
if [ $? -ne 0 ]; then
  echo "Error: Data verification failed."
  exit 1
fi

echo ""
echo "=== Setup Complete! ==="
echo "You can now start the application with:"
echo "npm start"
echo ""
echo "The application will be available at http://localhost:3000" 