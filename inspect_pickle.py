import pickle
import pprint
import numpy as np

with open('./public/subsetRecordings/CD 1/17. Gazelle du désert.pickle', 'rb') as f:
    data = pickle.load(f)
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