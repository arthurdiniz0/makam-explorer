#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:45:42 2025
tuning_analysis

@author: z11164
"""
import os, pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from constants import dataFolder, num_notes_in_octave, pitch_params, reference_freq
from common_tools import warp_hist_in_1_octave

def plot_hist_with_tonic(file_path, tonic_secs):
    pickle_file = os.path.join(dataFolder,file_path+'.pickle')
    with open(pickle_file, 'rb') as file:
        file_info = pickle.load(file) 
    tonic_start_ind = int(pitch_params['num_frames_per_sec'] * float(tonic_secs.split('-')[0]))
    tonic_stop_ind = int(pitch_params['num_frames_per_sec'] * float(tonic_secs.split('-')[1]))
    # Gather pitch series extracted using different methods
    pitches_tonic_region = np.empty((0,))
    for method in pitch_params['methods']:
        pitches_tonic_region = np.concatenate((pitches_tonic_region, 
                                                  file_info['pitch_'+method][tonic_start_ind:tonic_stop_ind]))
    # remove nan values
    pitches_tonic_region = pitches_tonic_region[~np.isnan(pitches_tonic_region)]
    
    # remove octave differences, put all in 110-220 Hz range
    #plt.figure()
    #plt.plot(pitches_tonic_region,'b')
    ref_freq = reference_freq * 4 # 220 Hz
    while (len(pitches_tonic_region[pitches_tonic_region > ref_freq]) > 0):
        pitches_tonic_region[pitches_tonic_region > ref_freq] /= 2
    
    while (len(pitches_tonic_region[pitches_tonic_region < ref_freq/2]) > 0):
        pitches_tonic_region[pitches_tonic_region < ref_freq/2] *= 2
    #plt.plot(pitches_tonic_region,'r')
    # Compute mean of the middle (1/3) part of the sorted array
    sorted_vals = np.sort(pitches_tonic_region)
    start = len(sorted_vals) // 3; end = 2 * start
    tonic_pitch = np.mean(sorted_vals[start:end])
    #plt.hlines(tonic_pitch, 0, len(pitches_tonic_region),'g')
        
    return tonic_pitch

def create_count_tables(df):
    # Create count tables
    counts_table = (
        df.groupby(['region', 'mode'])
        .size()
        .reset_index(name='count')
        .sort_values(by=['region', 'count'], ascending=[True, False])
    )

    counts_table.to_csv(os.path.join(dataFolder,'region_modes_count.csv'))

    counts_table = (
        df.groupby(['mode', 'region'])
        .size()
        .reset_index(name='count')
        .sort_values(by=['mode', 'count'], ascending=[True, False])
    )

    counts_table.to_csv(os.path.join(dataFolder,'mode_regions_count.csv'))

def align_hists(hist_array1, hist_array2):   
    len_array = hist_array1.shape[0]
    dist_per_shft = np.zeros((len_array,))
    for i in range(len_array):
        hist_array2_rolled = np.roll(hist_array2, i)
        # use L1-norm to compute distance
        dist_per_shft[i] = np.sum(np.abs(hist_array1-hist_array2_rolled))
    min_dist_roll_ind = np.argmin(dist_per_shft)
    return min_dist_roll_ind

def plot_aligned_hists(file_paths, all_hist_1_oct, plots_folder, maqam_region):
    # create folder if not exists
    if not os.path.exists(plots_folder):
        os.mkdir(plots_folder)
        
    # align 1 octave histograms with respect to each-other    
    num_hists = all_hist_1_oct.shape[0]
    for i in range(num_hists):    
        for i in range(num_hists-1):
            # shift all other(j) hists wrt i.th hist
            for j in range(i+1, num_hists):
                # find optimal shifts between log compressed versions of distributions
                shft = align_hists(np.log10(all_hist_1_oct[i]*1000), 
                                   np.log10(all_hist_1_oct[j]*1000))
                all_hist_1_oct[j] = np.roll(all_hist_1_oct[j], shft)
    
    # find max-valued peak index and shift all hists by that amount
    final_shft = np.argmax(all_hist_1_oct.mean(axis=0))
    max_num_chars = 40 # for limiting figure title length
    for i in range(num_hists):
        all_hist_1_oct[i] = np.roll(all_hist_1_oct[i], -final_shft)
        plt.plot(all_hist_1_oct[i])
        plt.grid()
        title = file_paths.iloc[i].replace(dataFolder,'')
        if len(title) > max_num_chars:
            title = title[:max_num_chars]+'...'
        plt.title(title)
        plt.savefig(os.path.join(plots_folder, maqam_region+str(i)+'.png'))
        plt.close()

# Read csv file, Drop rows where mode is NaN
all_metadata_csv_path = os.path.join(dataFolder, 'allfiles_metadata.csv')
df = pd.read_csv(all_metadata_csv_path)
df = df.dropna(subset=['mode'])

# retrieve unique maqams and regions
maqams = df['mode'].unique()
regions = df['region'].unique()

# create a dictionary of maqam-region file list
filelist_per_maqam_region = {}
for maqam in maqams:
    for region in regions:
        df_sub = df[(df['mode']==maqam) & (df['region']==region) & (df['vocal-only']==False)]
        if df_sub.shape[0] > 0: # add if ate least 1 file found
            filelist_per_maqam_region[maqam+'_'+region] = df_sub['path']

plots_folder = 'hist_plots'

# # Create aligned histogram plots per maqam_region
# for maqam_region, file_paths in filelist_per_maqam_region.items():
#     all_hist_1_oct = np.zeros((len(file_paths), num_notes_in_octave))
#     for ind, file_path in enumerate(file_paths):
#         pickle_file = os.path.join(dataFolder, file_path+'.pickle')
#         # Load content from the pickle file
#         with open(pickle_file, 'rb') as file:
#             file_info = pickle.load(file)
#         oct_warped_hist = warp_hist_in_1_octave(file_info['pitch_hist_values_mean'], num_notes_in_octave)
#         # store pitch distribution (scale histogram to have unit sum)
#         all_hist_1_oct[ind] = oct_warped_hist/np.sum(oct_warped_hist)
#     if all_hist_1_oct.shape[0] > 1:
#         plot_aligned_hists(file_paths, all_hist_1_oct, plots_folder, maqam_region)

# Create histogram plots with tonic labels if tonic_secs column is not nan
df_with_tonics = df.dropna(subset=['tonic_secs'])
for file_path, tonic_secs in zip(df_with_tonics['path'], df_with_tonics['tonic_secs']):
    tonic_pitch = plot_hist_with_tonic(file_path, tonic_secs)
    print(file_path[:20], tonic_secs, tonic_pitch, 'Hz')
    
