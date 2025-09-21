import os
import json
import pickle
import numpy as np
import argparse
from pathlib import Path

def convert_numpy_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
        # Handle NaN values and numpy number types
        if np.isnan(obj):
            return None
        return float(obj) if isinstance(obj, (np.float32, np.float64)) else int(obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_list(item) for item in obj]
    return obj

def process_directory(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all pickle files
    pickle_files = list(input_path.rglob("*.pickle"))
    print(f"Found {len(pickle_files)} pickle files")
    
    for pickle_path in pickle_files:
        try:
            # Read pickle file
            with open(pickle_path, 'rb') as f:
                data = pickle.load(f)
            
            # Convert numpy arrays to lists and handle NaN values
            converted_data = {}
            
            # Process pitch data
            for method in ['pitch_pyin', 'pitch_makam', 'pitch_crepe']:
                if method in data:
                    # Convert the pitch data to a list of [time, frequency] pairs
                    # Filter out NaN values
                    pitch_data = []
                    time_points = np.arange(len(data[method])) / 100  # Assuming 100Hz sampling rate
                    for t, f in zip(time_points, data[method]):
                        if not np.isnan(f):
                            pitch_data.append([float(t), float(f)])
                    converted_data[method] = pitch_data
            
            # Process histogram data - add the new oct_warped_hist_mean_wrt_tonic
            for key in ['pitch_hist_values', 'pitch_hist_edges', 'pitch_hist_values_mean', 'oct_warped_hist_mean_wrt_tonic']:
                if key in data:
                    converted_data[key] = convert_numpy_to_list(data[key])
            
            # Process method-specific histogram values
            for method in ['pyin', 'makam', 'crepe']:
                key = f'pitch_hist_values_{method}'
                if key in data:
                    converted_data[key] = convert_numpy_to_list(data[key])
                elif 'pitch_hist_values' in data and method == 'pyin':  # Default to pyin for backward compatibility
                    converted_data[key] = convert_numpy_to_list(data['pitch_hist_values'])
            
            # Process keyboard mapping data
            for key in ['mapped_key_freqs_hz', 'mapped_key_freqs_cent']:
                if key in data:
                    converted_data[key] = convert_numpy_to_list(data[key])
            
            # Process any other data that might be present
            for key in data:
                if key not in converted_data and key not in ['pitch_pyin', 'pitch_makam', 'pitch_crepe']:
                    converted_data[key] = convert_numpy_to_list(data[key])
            
            # Preserve relative directory structure
            relative_path = pickle_path.relative_to(input_path)
            json_path = output_path / relative_path.with_suffix('.json')
            
            # Create parent directories if they don't exist
            json_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(json_path, 'w') as f:
                json.dump(converted_data, f)
            
            print(f"Converted {pickle_path} -> {json_path}")
            print(f"Data keys found: {list(converted_data.keys())}")
            
        except Exception as e:
            print(f"Error processing {pickle_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert pickle files to JSON for Makam Explorer')
    parser.add_argument('--input_dir', type=str, default="data/cairo-congress-1932-features",
                        help='Input directory containing pickle files')
    parser.add_argument('--output_dir', type=str, default="public/data/cairo-congress-1932/analysis",
                        help='Output directory for JSON files')
    
    args = parser.parse_args()
    
    print(f"Processing files from {args.input_dir} to {args.output_dir}")
    process_directory(args.input_dir, args.output_dir) 