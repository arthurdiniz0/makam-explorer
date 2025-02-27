#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:35:06 2024

Collection of common functions

@author: barisbozkurt
"""
import os
import pickle
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

from constants import CENTS_IN_OCTAVE, num_notes_in_octave, region_artists, dataFolder, mode_name_map
from MB_tools import get_musicbrainz_metadata, get_recording_tags
from mutagen.easyid3 import EasyID3


def cents_to_hz(cents, reference_frequency=440):
    """
    Convert musical cents (with respect to reference_frequency) to Hertz.
    
    return: The frequency in Hz.
    """
    hz = reference_frequency * (2 ** (cents / 1200))
    return hz

def hz_to_cent_array(pitch_series_hz, ref_freq, min_freq=20.0):
    '''
    Converts pitch_series_hz values in Hertz to cents with 
    respect to ref_freq, setting all values below min_freq to NaN

    Parameters
    ----------
    pitch_series_hz : numpy.array
        Pitch series in Hertz.
    ref_freq : float
        Reference frequency (which will be represented as 0 cents point in fre. plane).
    min_freq : float, optional
        Lowest frequency in Hertz. Values below this are assumed as NaN. The default is 20.0.

    Returns
    -------
    numpy.array
        Pitch series in cents.

    '''
    pitch_series_hz[pitch_series_hz <= min_freq] = np.nan
    return np.log2(pitch_series_hz / ref_freq) * CENTS_IN_OCTAVE


def get_file_list(dataFolder, extension='.mp3'):
    '''
    Returns list of files in subfolders of dataFolder
    with given extension

    Parameters
    ----------
    dataFolder : str
        Path to main folder.
    extension : str, optional
        File extension. The default is '.mp3'.

    Returns
    -------
    file_list : list
        List of files (complete path).

    '''
    #Collecting file names
    file_list = []
    for root, dirs, files in os.walk(dataFolder):
        for file in files:
            if file.endswith(extension):
                file_name = os.path.join(root, file)
                file_list.append(file_name)
    return file_list

def warp_hist_in_1_octave(hist_series, num_notes_in_octave):
    '''
    Warps given histogram in a single octave. hist_series is assumed to
    be represent an octave with num_notes_in_octave points. 

    Parameters
    ----------
    hist_series : numpy.array
        Pitch histogram spanning several octaves.
    num_notes_in_octave : int
        Number of notes in an octave.

    Returns
    -------
    oct_warped_hist : numpy.array
        Warped version of the pitch histogram.

    '''
    oct_warped_hist = np.zeros((num_notes_in_octave,))
    for i in range(hist_series.size):
        oct_warped_hist[i%num_notes_in_octave] += hist_series[i]
    return oct_warped_hist

def plot_hist(pickle_file, jpeg_file, methods):
    '''
    Plots pitch histogram stored in file_info['pitch_hist_values_*']
    in the pickle file and saves the plot in jpeg_file

    Parameters
    ----------
    pickle_file : str
        Path to pickle file containing pitch histogram series for a recording.
    jpeg_file : str
        Path to jpeg file (created).
    methods : list
        List of pitch extraction methods.

    Returns
    -------
    None. Creates jpeg_file

    '''
    # Load content from the pickle file
    with open(pickle_file, 'rb') as file:
        file_info = pickle.load(file)

    plt.figure(figsize=(12,8))
    plt.subplot(2,1,1)
    colors = ['r','g','b','c']
    for c, method in zip(colors, methods):
        plt.plot(file_info['pitch_hist_edges'], file_info['pitch_hist_values_'+method], c, label=method)
    plt.plot(file_info['pitch_hist_edges'], file_info['pitch_hist_values_mean'], 'k', linewidth=2.5, label='mean')
    plt.grid(True)
    plt.legend(loc='upper right')

    plt.subplot(2,1,2)
    edges_1_oct = np.arange(0, CENTS_IN_OCTAVE, CENTS_IN_OCTAVE/num_notes_in_octave)
    for c, method in zip(colors, methods):
        oct_warped_hist = warp_hist_in_1_octave(file_info['pitch_hist_values_'+method], num_notes_in_octave)
        plt.plot(edges_1_oct, oct_warped_hist, c, label=method)
    
    oct_warped_hist = warp_hist_in_1_octave(file_info['pitch_hist_values_mean'], num_notes_in_octave)
    plt.plot(edges_1_oct, oct_warped_hist, 'k', linewidth=2.5, label='mean')
    
    # plot peaks and intervals
    maxima_positions = file_info['maxima_locs_cent'] 
             

    # Plot vertical lines at maxima locations and add text for index values
    y_max = np.max(oct_warped_hist)
    for x_max in maxima_positions:
        plt.axvline(x=x_max, color='k', linestyle='--')
        # Add text at the maximum position
        plt.text(x_max+5, y_max, f'{x_max:.2f}', color='black', ha='left', va='bottom', fontsize=12)
    
    # Calculate and plot distances between consecutive maxima
    mid_y = (np.max(oct_warped_hist) + np.min(oct_warped_hist)) / 2
    # delta_y = mid_y/5
    for i in range(len(maxima_positions) - 1):
        # Calculate distance
        distance = file_info['intervals'][i]
        # Midpoint between two maxima for text placement
        mid_x = (maxima_positions[i] + maxima_positions[i + 1]) / 2
        # mid_y += delta_y * (-1)**i
        
        # Annotate the distance between peaks
        plt.text(mid_x, mid_y, f'{distance:.1f}', color='blue', ha='center', va='bottom', fontsize=12)

    
    plt.grid(True)
    # plt.legend(loc='upper right')
    plt.xlabel('Cents wrt to ref-freq:55Hz')
    plt.ylabel('Num. of Occurences')    
    plt.savefig(jpeg_file, dpi=100)  # dpi can be adjusted for higher quality
    plt.close()

    
def moving_average_3_point(arr):
    """
    Smooth the array using a 3-point moving average without shifting in time.
    
    Parameters:
    arr (numpy.ndarray): Input array to smooth.
    
    Returns:
    numpy.ndarray: Smoothed array.
    """
    smoothed_arr = np.zeros_like(arr)  # Initialize an array of the same size

    # Handle the boundary cases
    smoothed_arr[0] = (arr[0] + arr[1]) / 2  # First point: average of itself and the next point
    smoothed_arr[-1] = (arr[-1] + arr[-2]) / 2  # Last point: average of itself and the previous point

    # Apply the 3-point moving average for the rest of the points
    for i in range(1, len(arr) - 1):
        smoothed_arr[i] = (arr[i - 1] + arr[i] + arr[i + 1]) / 3

    return smoothed_arr

def find_maxima_positions(average_hist):
    # Find maxima positions using 3-point polynomial interpolation 
    
    # Find local maxima using argrelextrema
    maxima_indices = argrelextrema(average_hist, np.greater)[0]
    
    maxima_positions = []

    for idx in maxima_indices:
        # Make sure there are at least two neighbors for interpolation
        if idx > 0 and idx < len(average_hist) - 1:
            # Points for interpolation: (x0, y0), (x1, y1), (x2, y2)
            x0, x1, x2 = idx - 1, idx, idx + 1
            y0, y1, y2 = average_hist[x0], average_hist[x1], average_hist[x2]

            # Coefficients for the quadratic polynomial y = ax^2 + bx + c
            a = (y0 - 2 * y1 + y2) / 2
            b = (y2 - y0) / 2
            # c = y1

            # Vertex (maximum position) of the parabola: x = -b / (2a)
            if a != 0:  # Check to prevent division by zero
                x_max = x1 - b / (2 * a)
            else:
                x_max = x1  # If a is 0, use the central point as the maximum

            maxima_positions.append(x_max)
    
    return np.array(maxima_positions)


def shift_rotate_histogram(hist_array):
    '''Shift-rotates histogram to move minima to index 0
    It is assumed that the histogram spans (i.e. warped in) a single octave
    Used for detecting maximas, avoiding the case a peak appears at index 0
    
    Returns
    -------
    numpy.array
        Rotated histogram.
    int
        Shift amount
    '''
    
    # Find the index of the minimum value
    min_index = np.argmin(hist_array)
    
    # Shift-rotate the array such that the minimum value is at index 0
    return np.roll(hist_array, -min_index), min_index
    


def compute_maxima_locs_from_hist(file_info, plot_on=False):
    '''
    Computes maxima locations in cents from the 
    given histogram (stored in file_info['pitch_hist_values_mean'])

    Parameters
    ----------
    file_info : dict
        Dictionary containing all parameters of a recording.
    plot_on : bool, optional
        Flag for setting plotting on/off. The default is False.

    Returns
    -------
    numpy.array
        Maxima locations in cents.

    '''
        
    # average_hist = file_info['pitch_hist_values_mean']
    oct_warped_hist = warp_hist_in_1_octave(file_info['pitch_hist_values_mean'], num_notes_in_octave)
    # shift minima to index 0 not to miss peak at boundaries of the histogram
    oct_warped_hist_shft, min_index = shift_rotate_histogram(oct_warped_hist)
    # find maxima locations (shifted version)
    maxima_positions_shft = find_maxima_positions(oct_warped_hist_shft)
    # revert shifting
    maxima_positions = np.sort(np.mod(maxima_positions_shft + min_index, num_notes_in_octave))
    
    if plot_on:
        # Plot the array
        plt.subplot(2,1,1)
        plt.plot(oct_warped_hist_shft)
        plt.xlabel('Index')
        plt.ylabel('Value')
        
        # Plot vertical lines at maxima locations and add text for index values
        for x_max in maxima_positions_shft:
            plt.axvline(x=x_max, color='r', linestyle='--')
            # Add text at the maximum position
            y_max = np.interp(x_max, np.arange(len(oct_warped_hist)), oct_warped_hist)  # Interpolate to get the y-value for text placement
            plt.text(x_max, y_max, f'{x_max:.2f}', color='red', ha='left', va='bottom')
        
        # Calculate and plot distances between consecutive maxima
        mid_y = (np.max(oct_warped_hist) + np.min(oct_warped_hist)) / 2
        delta_y = mid_y/5
        for i in range(len(maxima_positions_shft) - 1):
            # Calculate distance
            distance = maxima_positions_shft[i + 1] - maxima_positions_shft[i]
            # Midpoint between two maxima for text placement
            mid_x = (maxima_positions_shft[i] + maxima_positions_shft[i + 1]) / 2
            mid_y += delta_y * (-1)**i
            
            # Annotate the distance between peaks
            plt.text(mid_x, mid_y, f'{distance:.2f}', color='blue', ha='center', va='bottom', fontsize=10)
        
        plt.subplot(2,1,2)
        plt.plot(oct_warped_hist)
        plt.xlabel('Index')
        plt.ylabel('Value')
        
        # Plot vertical lines at maxima locations and add text for index values
        for x_max in maxima_positions:
            plt.axvline(x=x_max, color='r', linestyle='--')
            # Add text at the maximum position
            y_max = np.interp(x_max, np.arange(len(oct_warped_hist)), oct_warped_hist)  # Interpolate to get the y-value for text placement
            plt.text(x_max, y_max, f'{x_max:.2f}', color='red', ha='left', va='bottom')
        
        # Calculate and plot distances between consecutive maxima
        mid_y = (np.max(oct_warped_hist) + np.min(oct_warped_hist)) / 2
        delta_y = mid_y/5
        for i in range(len(maxima_positions) - 1):
            # Calculate distance
            distance = maxima_positions[i + 1] - maxima_positions[i]
            # Midpoint between two maxima for text placement
            mid_x = (maxima_positions[i] + maxima_positions[i + 1]) / 2
            mid_y += delta_y * (-1)**i
            
            # Annotate the distance between peaks
            plt.text(mid_x, mid_y, f'{distance:.2f}', color='blue', ha='center', va='bottom', fontsize=10)
        plt.show()
    
    maxima_locs_cent = maxima_positions*CENTS_IN_OCTAVE/num_notes_in_octave
    return maxima_locs_cent

        
def pure_sin_resynth(f0track, fsample, pitch_sca_fact, dur_sca_fact):
    '''Sinosoidal sythesis from pitch series
    @author: barisbozkurt'''
    f0track = f0track * pitch_sca_fact

    # It is assumed that f0s are listed for each 10msec
    frame_len = 10e-3 * dur_sca_fact  # in seconds

    # Frame by frame synthesis
    t = np.arange(0, frame_len + 1/fsample, 1/fsample)  # we lose one sample during phase continuity and flushing to output
    frame_len_samp = len(t)  # in number of samples
    fade_out_env = np.linspace(1, 0, frame_len_samp)
    fade_in_env = np.linspace(0, 1, frame_len_samp)
    pha = 0

    total_len = len(f0track) * frame_len_samp
    syn_sound = np.zeros(total_len)

    for k in range(len(f0track)):
        if f0track[k] > 30:
            frame = np.cos(2 * np.pi * f0track[k] * t + pha)
        else:
            frame = np.zeros_like(t)

        # Choose among cos(theta) and cos(-theta)
        ph = np.arccos(frame[-2:])
        if ph[0] > ph[1]:
            pha = -ph[1]
        else:
            pha = ph[1]

        # FADE IN-OUT OPERATIONS TO AVOID CLICKS
        if k == 0:
            frame *= fade_in_env
        else:
            if f0track[k-1] < 30:
                frame *= fade_in_env

        if k == len(f0track) - 1:
            frame *= fade_out_env
        else:
            if f0track[k+1] < 30:
                frame *= fade_out_env

        # Insert frame into the output signal
        syn_sound[k * (frame_len_samp-1):(k+1) * (frame_len_samp-1)] = frame[1:]

    return syn_sound

def write_f0series_to_file(pickle_file, outfile, series_name, t_steps=0.01):
    '''
    Dumps f0-series to file so that it can be loaded and viewed in tools like
    sonic-visualizer

    Parameters
    ----------
    pickle_file : str
        Path to pickle file.
    outfile : str
        Path to output file.
    series_name : str
        Key in file_info that provides access to the series.
    t_steps : float
        Time steps in seconds. Used to create the time instant series 

    Returns
    -------
    None. Creates outfile (in text format)

    '''
    # Load content from the pickle file
    with open(pickle_file, 'rb') as file:
        file_info = pickle.load(file)
    f0series = file_info[series_name]
    t = np.arange(t_steps/2, (f0series.shape[0]+0.5)*t_steps, t_steps)
    
    with open(outfile, 'w') as f:
        for time_s, freq in zip(t, f0series):
            if np.isnan(freq):
                freq = 0
            f.write(f"{time_s:.2f}, {freq:.2f}\n")

def write_all_f0_series_to_files(pickle_file):
    '''
    Calls write_f0series_to_file for all pitch series to create all 
    pitch series files for viewing with external tools

    Parameters
    ----------
    pickle_file : str
        Path to pickle file.

    Returns
    -------
    None. Creates files at the same location as the pickle_file

    '''
    outfile = pickle_file.replace('.pickle','.csv')
    f0series_names = ['pitch_pyin','pitch_crepe', 'pitch_makam']
    for name in f0series_names:
        outfile_series = outfile.replace('.csv','.'+name.replace('pitch_','')+'.csv')
        write_f0series_to_file(pickle_file, outfile_series, name)

def get_artist_list_for_regions(region_list):
    '''
    region_artists dictionary comes from constants.py which reads 
    region_artists.json to get map of regiones versus artists-list

    Parameters
    ----------
    region_list : list of str
        List of regions.

    Returns
    -------
    artist_list : list of str
        List of artist names for the regions given in region_list.

    '''
    artist_list = []
    for region in region_list:
        artist_list += region_artists[region]
    return artist_list

def get_recording_artist_region(file_info):
    ''' Returns recording artist name from file_info
    This function is needed because musicBrainz may store this info under different dictionary keys
    Options:
        file_info['mb_metadata']['recording']['artist-credit'][0]['name']
        file_info['mb_metadata']['recording']['artist-credit'][0]['artist']['name']
    
    '''
    recording_artist = ''
    if 'name' in file_info['mb_metadata']['recording']['artist-credit'][0]:
        recording_artist = file_info['mb_metadata']['recording']['artist-credit'][0]['name']
    elif 'artist' in file_info['mb_metadata']['recording']['artist-credit'][0]:
        recording_artist = file_info['mb_metadata']['recording']['artist-credit'][0]['artist']['name']
    
    recording_region = ''
    for region, artists in region_artists.items():
        if recording_artist in artists:
            recording_region = region
    
    return recording_artist, recording_region

def update_pickle_metadata(pickle_file, track_mbid):
    '''
    Updates pickle file metadata with info retrieved on musicBrainz using
    track_mbid
    '''        
    # Load content from the pickle file
    with open(pickle_file, 'rb') as file:
        file_info = pickle.load(file)
    
    file_info['mb_metadata'] = get_musicbrainz_metadata(track_mbid)
    file_info['mb_tags'] = get_recording_tags(track_mbid)
    file_info['mbid'] = track_mbid
    # Save extended content to the pickle file
    with open(pickle_file, 'wb') as file:
        pickle.dump(file_info, file)        

def update_tags_from_musicbrainz():
    '''Function to call after tags are edited in musicbrainz
    Only updates tags'''
    
    pickle_files_list = get_file_list(dataFolder, extension='.pickle')

    for i, pickle_file in enumerate(pickle_files_list):
        if i%20 == 0:
            print('Updating file index:', i, 'of', len(pickle_files_list))
        
        with open(pickle_file, 'rb') as file:
            file_info = pickle.load(file)
        
        # update tags
        file_info['mb_tags'] = get_recording_tags(file_info['mbid'])
        
        # Save extended content to the pickle file
        with open(pickle_file, 'wb') as file:
            pickle.dump(file_info, file)
        

def update_id3_tags(file_path, metadata):
    """
    Update ID3 tags of an MP3 file using metadata from MusicBrainz.
    """
    # Retrieve cd-index and track-index from file name
    CD_index = file_path.replace(dataFolder,'').replace('CD ','').split('/')[0]
    track_index = file_path.replace(dataFolder,'').replace('CD ','').split('/')[1].split('.')[0]

    
    try:
        audio = EasyID3(file_path)
    except Exception as e:
        print(f"Error reading ID3 tags for {file_path}: {e}")
        return

    # Map metadata fields to ID3 tags
    try:
        audio["album"] = metadata['releases'][0]['title']
        audio["title"] = metadata.get("title", "")
        audio["artist"] = ", ".join(
            artist["name"] for artist in metadata.get("artist-credit", [])
        )
        audio["musicbrainz_trackid"] = metadata.get("id", "")
        audio["musicbrainz_albumid"] = metadata.get("releases", [{}])[0].get("id", "")
        audio['discnumber'] = CD_index+'/18'
        audio['tracknumber'] = track_index
        # Save changes
        audio.save()
        print(f"Updated ID3 tags for CD{CD_index}-{track_index}")
    except Exception as e:
        print(f"Error updating ID3 tags for {file_path}: {e}")

def convert_tags_to_dict(tags):
    '''
    Converts tags in list form to dictionary form

    Parameters
    ----------
    tags : list
        List of tags, example: ['form: qasida', 'mode: husayni', 'rhythm: free'].

    Returns
    -------
    tag_dict : dict
        Tag dictionary, example: {'form': 'qasida', 'mode': 'husayni', 'rhythm': 'free'} .

    '''
    tag_dict = {}
    for tag in tags:
        parts = tag.split(': ')
        if len(parts) == 2:
            key = parts[0].strip()
            if key == 'maqam':
                key = 'mode'
            tag_dict[key] = parts[1].strip()

    # merge modes if there exist more than one
    if ('mode1' in tag_dict) and ('mode2' in tag_dict):
        tag_dict['mode'] = tag_dict['mode1'] + ', ' + tag_dict['mode2']
    
    if 'mode' not in tag_dict:
        tag_dict['mode'] = 'NA'
        
    # converting rare variants in mode names
    for key, value in mode_name_map.items():
        if tag_dict['mode'] == key:
            tag_dict['mode'] = value
        
    return tag_dict

def save_allMetadata_to_file(dataFolder='../AudioCollection/CDsWithTags/'):
    
    columns = ['path','link','mb_trackTitle','tags','mode','vocal-only','tonic_secs','artist','region']
    df = pd.DataFrame(columns=columns)
    
    # Get pickle files list    
    pickle_files_list = get_file_list(dataFolder, extension='.pickle')
    
    for pickle_file in pickle_files_list:
        
        with open(pickle_file, 'rb') as file:
            file_info = pickle.load(file)

        recording_path = pickle_file.replace(dataFolder,'').replace('.pickle','')        
        recording_mbid = file_info['mbid']
        recording_mb_trackTitle = file_info['mb_metadata']['recording']['title']
        recording_tags = file_info['mb_tags']
        recording_tags_dict = convert_tags_to_dict(recording_tags)
        recording_artist, recording_region = get_recording_artist_region(file_info)
        
        row_data = {'path': recording_path, 
                    'link': 'https://musicbrainz.org/recording/'+recording_mbid, 
                    'mb_trackTitle': recording_mb_trackTitle, 
                    'tags': recording_tags,
                    'mode': recording_tags_dict['mode'],
                    'vocal-only': ('vocal-only' in recording_tags),
                    'tonic_secs': recording_tags_dict['tonic_secs'] if 'tonic_secs' in recording_tags_dict else None,
                    'artist': recording_artist, 
                    'region': recording_region}
        
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    
    df_sorted = df.sort_values(by='path')
    df_sorted.to_csv(os.path.join(dataFolder,'allfiles_metadata.csv'), index=False)

        

save_allMetadata_to_file()