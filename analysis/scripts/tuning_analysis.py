#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:45:42 2025
A demonstrative script to create mean histogram plots from
using the histograms in pickle files of the dataset

@author: barisbozkurt
"""
import os, pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from constants import dataFolder, CENTS_IN_OCTAVE, num_notes_in_octave

def plot_hist_with_grid(oct_warped_hists_list, jpeg_file, tonic_freq=None, num_files_in_average=0, legend_strs=[]):
    '''
    Plot histograms on a grid 

    Parameters
    ----------
    oct_warped_hists_list : list of arrays
        List of histograms to be plotted.
    jpeg_file : str
        Path to output image file for the plot.
    tonic_freq : float, optional
        Tonic frequency in hertz. The default is None.
    num_files_in_average : int, optional
        Number of files used in computing the mean histogram. The default is 0.
    legend_strs : str, optional
        Legends for the plot if more than one histograms plotted. The default is [].

    Returns
    -------
    None.

    '''
    
    plt.figure(figsize=(12,4))
    
    # plot grids
    max_val = 1.2 # maximum value for the histogram plot
    x_ax_major = np.arange(0,1200,100)
    x_ax_minor = np.arange(0,1200,20)
    plt.vlines(x_ax_minor, 0, max_val, colors='g', linestyles='dashed')
    plt.vlines(x_ax_major, 0, max_val, colors='k', linestyles='solid')

    colors = ['b','k','r','c','g','m']
    for ind in range(len(oct_warped_hists_list)):
        oct_warped_hist = oct_warped_hists_list[ind]
        
        # normalize to unit max for obtaining plots easier to compare visually
        oct_warped_hist /= max(oct_warped_hist) 
        if legend_strs:
            plt.plot(edges_1_oct, oct_warped_hist, colors[ind], label=legend_strs[ind])
        else:
            plt.plot(edges_1_oct, oct_warped_hist, 'b')#, label='tonic_aligned')
    
    if tonic_freq: # tonic freq. specified while calling this function
        plt.xlabel(f"Cents wrt to tonic-freq:{tonic_freq:.2f} Hz")
    else: # tonic freq. not specified
        if legend_strs: # various histograms with legend labels to be plotted
            plt.xlabel("Cents wrt to tonic")
        else: # single histogram to be plotted
            plt.xlabel(f"Cents wrt to tonic, number of files: {num_files_in_average}")
    plt.grid(True)
    if legend_strs:
        plt.legend(loc='upper right')
    
    plt.ylabel('Normalized Num. of Occurences')   
    plt.savefig(jpeg_file, dpi=200)  # dpi can be adjusted for higher quality
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

# Plot-files output folder
plots_folder = '../AudioCollection/CDsWithTags/tonic_aligned_hists'

if not os.path.exists(plots_folder):
    os.mkdir(plots_folder)

# exclude list: defined via visual check of the histograms: tonic labels may not be reliable for these recordings
exclude_list = ['CD 6/11.','CD 6/12.','CD 8/04.','CD 15/01.','CD 15/05.','CD 18/04.']

# Create aligned histogram plots per maqam_region
edges_1_oct = np.arange(0, CENTS_IN_OCTAVE, CENTS_IN_OCTAVE/num_notes_in_octave)
hist_4_maqam_region = {}
numFiles_4_maqam_region = {}
for maqam_region, file_paths in filelist_per_maqam_region.items():
    average_hist = np.zeros((num_notes_in_octave,)) # mean tonic aligned histogram for maqam-region
    num_files_in_average = 0
    for ind, file_path in enumerate(file_paths):
        if not any(excluded in file_path for excluded in exclude_list):

            # Load content from the pickle file
            pickle_file = os.path.join(dataFolder, file_path+'.pickle')
            with open(pickle_file, 'rb') as file:
                file_info = pickle.load(file)            
            
            # if octave warped wrt tonic available, plot and add to average
            if 'oct_warped_hist_mean_wrt_tonic' in file_info:
                jpeg_file = os.path.join(plots_folder, 
                                         maqam_region+file_info['file_name'].split('.')[0].replace('/','_').replace(' ','')+'.jpeg')
                tonic_freq = file_info['tonic_pitch_hz']
                plot_hist_with_grid([file_info['oct_warped_hist_mean_wrt_tonic']], jpeg_file, tonic_freq)
                
                
                # add current histogram to average histogram for maqam_region
                average_hist += (file_info['oct_warped_hist_mean_wrt_tonic']/np.sum(file_info['oct_warped_hist_mean_wrt_tonic']))
                num_files_in_average += 1
    
    # create a plot for mean histogram for the maqam_region
    if np.sum(average_hist) > 0:
        jpeg_file = os.path.join(plots_folder, maqam_region+'_mean.jpeg')
        plot_hist_with_grid([average_hist], jpeg_file,[],num_files_in_average)
        hist_4_maqam_region[maqam_region] = average_hist
        numFiles_4_maqam_region[maqam_region] = num_files_in_average
        

# Plot superimposed regional histogram plots for each maqam
for maqam in maqams:
    legend_strs = []
    hists = []
    for maqam_region in hist_4_maqam_region.keys():
        if maqam+'_' in maqam_region:
            legend_str = maqam_region.replace(maqam+'_','') + ' ' + str(numFiles_4_maqam_region[maqam_region]) + ' recs'
            legend_strs.append(legend_str)
            hists.append(hist_4_maqam_region[maqam_region])
    if len(legend_strs) > 1:
        jpeg_file = os.path.join(plots_folder, maqam+'_regions.jpeg')
        plot_hist_with_grid(hists, jpeg_file,[],-1, legend_strs)
        
# All plots stored in  plots_folder, check them out           
            
            