import os
import json
import pickle
import numpy as np
from pathlib import Path

def convert_numpy_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.float32) or isinstance(obj, np.float64):
        # Handle NaN values
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_list(item) for item in obj]
    return obj

def process_directory(base_dir):
    base_path = Path(base_dir)
    
    # Find all pickle files
    pickle_files = list(base_path.rglob("*.pickle"))
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
            
            # Process histogram data
            for key in ['pitch_hist_values', 'pitch_hist_edges', 'pitch_hist_values_mean']:
                if key in data:
                    converted_data[key] = convert_numpy_to_list(data[key])
            
            # Process any other data that might be present
            for key in data:
                if key not in converted_data and key not in ['pitch_pyin', 'pitch_makam', 'pitch_crepe']:
                    converted_data[key] = convert_numpy_to_list(data[key])
            
            # Save as JSON
            json_path = pickle_path.with_suffix('.json')
            with open(json_path, 'w') as f:
                json.dump(converted_data, f)
            
            print(f"Converted {pickle_path} -> {json_path}")
            print(f"Data keys found: {list(converted_data.keys())}")
            
        except Exception as e:
            print(f"Error processing {pickle_path}: {e}")

if __name__ == "__main__":
    process_directory("public/subsetRecordings") 