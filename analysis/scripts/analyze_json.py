import json
import os
from pathlib import Path
import numpy as np

def analyze_json_structure(json_data, prefix=''):
    """Recursively analyze the structure of JSON data."""
    if isinstance(json_data, dict):
        structure = {}
        for key, value in json_data.items():
            if isinstance(value, (dict, list)):
                structure[key] = analyze_json_structure(value, prefix + '  ')
            else:
                # For non-container types, store the type and a sample value
                structure[key] = {
                    'type': type(value).__name__,
                    'sample': str(value)[:100] + '...' if isinstance(value, str) and len(str(value)) > 100 else value
                }
        return structure
    elif isinstance(json_data, list):
        if not json_data:
            return {'type': 'list', 'length': 0}
        # For lists, analyze the first few items
        sample_size = min(3, len(json_data))
        samples = json_data[:sample_size]
        return {
            'type': 'list',
            'length': len(json_data),
            'sample_items': [analyze_json_structure(item, prefix + '  ') for item in samples]
        }
    return {'type': type(json_data).__name__, 'value': json_data}

def analyze_pitch_data(data, method_name):
    """Analyze pitch data for a specific method."""
    if method_name not in data:
        return None
    
    pitch_data = data[method_name]
    if not pitch_data:
        return None
    
    # Extract frequencies and times
    times = [point[0] for point in pitch_data]
    freqs = [point[1] for point in pitch_data]
    
    return {
        'total_points': len(pitch_data),
        'duration': max(times) - min(times),
        'freq_range': {
            'min': min(freqs),
            'max': max(freqs),
            'mean': sum(freqs) / len(freqs)
        },
        'sample_rate': len(pitch_data) / (max(times) - min(times)) if len(times) > 1 else None
    }

def analyze_histogram_data(data):
    """Analyze histogram data."""
    if 'pitch_hist_values' not in data or 'pitch_hist_edges' not in data:
        return None
    
    hist_values = data['pitch_hist_values']
    hist_edges = data['pitch_hist_edges']
    
    # Find peaks (local maxima)
    peaks = []
    for i in range(1, len(hist_values) - 1):
        if hist_values[i] > hist_values[i-1] and hist_values[i] > hist_values[i+1]:
            if hist_values[i] > max(hist_values) * 0.1:  # Only peaks above 10% of max
                peaks.append({
                    'cent': hist_edges[i],
                    'value': hist_values[i]
                })
    
    peaks.sort(key=lambda x: x['value'], reverse=True)
    
    return {
        'num_bins': len(hist_values),
        'cent_range': {
            'min': min(hist_edges),
            'max': max(hist_edges)
        },
        'significant_peaks': peaks[:5]  # Top 5 peaks
    }

def analyze_json_file(file_path):
    """Analyze a single JSON file and return its structure."""
    print(f"\n{'='*80}")
    print(f"Analyzing {file_path}...")
    print(f"{'='*80}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Basic file info
        print("\nFile Statistics:")
        print(f"File size: {os.path.getsize(file_path) / (1024*1024):.2f} MB")
        print(f"Number of top-level keys: {len(data)}")
        print(f"Available keys: {', '.join(data.keys())}")
        
        # Analyze pitch detection methods
        print("\nPitch Detection Methods:")
        for method in ['pitch_pyin', 'pitch_makam', 'pitch_crepe']:
            pitch_analysis = analyze_pitch_data(data, method)
            if pitch_analysis:
                print(f"\n{method.upper()}:")
                print(f"  Total points: {pitch_analysis['total_points']}")
                print(f"  Duration: {pitch_analysis['duration']:.2f} seconds")
                print(f"  Frequency range: {pitch_analysis['freq_range']['min']:.1f}Hz - {pitch_analysis['freq_range']['max']:.1f}Hz")
                print(f"  Mean frequency: {pitch_analysis['freq_range']['mean']:.1f}Hz")
                print(f"  Effective sample rate: {pitch_analysis['sample_rate']:.1f}Hz")
        
        # Analyze histogram data
        hist_analysis = analyze_histogram_data(data)
        if hist_analysis:
            print("\nHistogram Analysis:")
            print(f"Number of bins: {hist_analysis['num_bins']}")
            print(f"Cent range: {hist_analysis['cent_range']['min']:.1f} - {hist_analysis['cent_range']['max']:.1f} cents")
            print("\nTop 5 peaks (in cents):")
            for i, peak in enumerate(hist_analysis['significant_peaks'], 1):
                print(f"  {i}. {peak['cent']:.1f} cents (strength: {peak['value']:.3f})")
        
        # Check for additional data
        other_keys = [k for k in data.keys() if not k.startswith('pitch_') and k not in 
                     ['pitch_hist_values', 'pitch_hist_edges', 'pitch_hist_values_mean']]
        if other_keys:
            print("\nAdditional Data Fields:")
            for key in other_keys:
                value = data[key]
                if isinstance(value, list):
                    print(f"  {key}: List with {len(value)} items")
                    if len(value) > 0:
                        print(f"    Sample: {value[0]}")
                else:
                    print(f"  {key}: {type(value).__name__}")
                    
    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")

def main():
    # Path to the recordings directory
    recordings_path = Path('public/subsetRecordings')
    
    # Find all JSON files recursively
    json_files = list(recordings_path.rglob('*.json'))
    
    if not json_files:
        print("No JSON files found in the specified directory.")
        return
    
    print(f"Found {len(json_files)} JSON files")
    
    # Analyze each JSON file
    for json_file in json_files:
        analyze_json_file(json_file)

if __name__ == "__main__":
    main() 