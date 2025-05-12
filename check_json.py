import os
import sys
import json
import argparse
from pathlib import Path

def check_audio_files(audio_dir):
    """Check if audio files exist in the specified directory"""
    audio_dir = Path(audio_dir)
    if not audio_dir.exists():
        print(f"ERROR: Audio directory {audio_dir} does not exist!")
        return False
    
    audio_files = list(audio_dir.rglob("*.mp3"))
    if len(audio_files) == 0:
        print(f"ERROR: No MP3 files found in {audio_dir}!")
        return False
    
    print(f"SUCCESS: Found {len(audio_files)} MP3 files in {audio_dir}")
    for i, file in enumerate(audio_files[:5]):  # Show first 5 files
        print(f"  {i+1}. {file.relative_to(audio_dir)}")
    
    if len(audio_files) > 5:
        print(f"  ... and {len(audio_files) - 5} more files")
    
    return True

def check_json_files(json_dir):
    """Check if JSON files exist and have the correct structure"""
    json_dir = Path(json_dir)
    if not json_dir.exists():
        print(f"ERROR: JSON data directory {json_dir} does not exist!")
        return False
    
    json_files = list(json_dir.rglob("*.json"))
    if len(json_files) == 0:
        print(f"ERROR: No JSON files found in {json_dir}!")
        return False
    
    print(f"SUCCESS: Found {len(json_files)} JSON files in {json_dir}")
    
    # Check contents of a sample file
    sample_file = json_files[0]
    print(f"Checking sample file: {sample_file}")
    
    try:
        with open(sample_file, 'r') as f:
            data = json.load(f)
            
        required_keys = ['pitch_hist_edges', 'mapped_key_freqs_hz', 'mapped_key_freqs_cent']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"WARNING: The following required keys are missing: {', '.join(missing_keys)}")
            print("The file may not contain all necessary data for the application to work properly.")
        else:
            print("SUCCESS: Sample file contains all required data keys.")
            print(f"Data keys found: {', '.join(sorted(data.keys())[:10])}...")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to parse JSON file {sample_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Check if required data files exist for Makam Explorer')
    parser.add_argument('--audio_dir', type=str, default="public/subsetRecordings",
                        help='Directory containing MP3 files')
    parser.add_argument('--json_dir', type=str, default="public/pitch_data",
                        help='Directory containing JSON pitch data files')
    
    args = parser.parse_args()
    
    print("=== Makam Explorer Data Validation ===")
    
    audio_ok = check_audio_files(args.audio_dir)
    json_ok = check_json_files(args.json_dir)
    
    if audio_ok and json_ok:
        print("\n✅ All data files are present and valid!")
        print("You can now run 'npm start' to launch the application.")
        return 0
    else:
        print("\n❌ Some required data files are missing or invalid.")
        print("Please follow the setup instructions in the README.md file.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 