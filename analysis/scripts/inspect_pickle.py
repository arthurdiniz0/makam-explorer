import pickle
import pprint
import numpy as np

with open('./public/subsetRecordings/subset_recordings_pickle/CD 1/17. Gazelle du désert.pickle', 'rb') as f:
    data = pickle.load(f)
    print("\nNew Keyboard Mapping Data:")
    if 'mapped_key_freqs_hz' in data:
        print("\nmapped_key_freqs_hz:", data['mapped_key_freqs_hz'])
    if 'mapped_key_freqs_cent' in data:
        print("\nmapped_key_freqs_cent:", data['mapped_key_freqs_cent'])
    
    print("\nHistogram data:")
    print("pitch_hist_values:", np.array(data['pitch_hist_values']).shape if 'pitch_hist_values' in data else None)
    print("pitch_hist_edges:", np.array(data['pitch_hist_edges']).shape if 'pitch_hist_edges' in data else None)
    print("pitch_hist_values_mean:", np.array(data['pitch_hist_values_mean']).shape if 'pitch_hist_values_mean' in data else None)
    
    if 'pitch_hist_values' in data:
        print("\nSample of pitch_hist_values:", data['pitch_hist_values'][:10])
    if 'pitch_hist_edges' in data:
        print("\nSample of pitch_hist_edges:", data['pitch_hist_edges'][:10])
    if 'pitch_hist_values_mean' in data:
        print("\nSample of pitch_hist_values_mean:", data['pitch_hist_values_mean'][:10])
    
    print("\nAll available keys:", list(data.keys())) 