#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:11:05 2024

Script to map estimated frequencies to computr keyboard for sonification-testing

Script that adds two new fields to pickle files:
    - mapped_key_freqs_cent
    - mapped_key_freqs_hz
Via:
    - finding best constant shift amount for matching of 12TET 
        grid to note-intervals estimated using histograms
    - after the constant shift, replace values with their closest
        in the estimated values list

@author: barisbozkurt
"""

import numpy as np
import pickle

from constants import reference_freq, num_notes_in_octave, CENTS_IN_OCTAVE, dataFolder
from common_tools import cents_to_hz, get_file_list

def optimal_shift(locs_cent_arr1: np.ndarray, locs_cent_arr2: np.ndarray) -> int:
    """
    Finds the optimal shift amount between two binary arrays that minimizes the edit (Hamming) distance.
    
    Parameters:
        locs_cent_arr1 (np.ndarray): First array containing peak freq. in cents.
        locs_cent_arr2 (np.ndarray): Second array containing peak freq. in cents.
        
    Returns:
        int: Optimal shift amount in cents that minimizes the edit distance.
    """
    
    # create simplified distribution-like representations for peak frequencies
    arr1 = create_tuning_array(locs_cent_arr1, num_notes_in_octave)
    arr2 = create_tuning_array(locs_cent_arr2, num_notes_in_octave)
    
    # smooth arrays to allow better match
    arr1 = np.convolve(np.array([0.25, 0.5, 0.25]), arr1)
    arr2 = np.convolve(np.array([0.25, 0.5, 0.25]), arr2)
    
    min_distance = float('inf')
    optimal_shift_amount = 0
    
    for shift in range(len(arr1)):
        rotated_arr1 = np.roll(arr1, shift)
        # compute euclidean distance
        distance = np.linalg.norm(rotated_arr1 - arr2)
        
        
        if distance < min_distance:
            min_distance = distance
            optimal_shift_amount = shift

    # plt.figure()
    # rotated_arr1 = np.roll(arr1, optimal_shift_amount)
    # plt.plot(np.arange(0,1240,20), rotated_arr1,'b-o')
    # plt.plot(np.arange(0,1240,20), arr2,'r--');plt.title(f'shft:{optimal_shift_amount},dist:{min_distance}')
    # plt.grid(); 
    
    optimal_shift_cents = optimal_shift_amount * (CENTS_IN_OCTAVE/num_notes_in_octave)
    return optimal_shift_cents, np.roll(arr1, optimal_shift_amount), arr2 

def create_tuning_array(locs_cent, array_len):
    arr = np.zeros(array_len)
    step_size_cents = CENTS_IN_OCTAVE / array_len
    inds = np.round(locs_cent / step_size_cents).astype('int')
    arr[inds%array_len] = 1
    return arr

def map_2_closest(arr1, arr2):
    '''
    Replaces avlues in arr1 with the closest values in arr2

    Parameters
    ----------
    arr1 : numpy array
        Note frequencies (theoretical)
    arr2 : numpy array
        Note frequencies (measured)

    Returns
    -------
    None. Modifies arr1

    '''
    for val in arr2:
        arr1[np.argmin(np.abs(arr1-val))] = val
    # check if all values in arr2 is represented
    for val in arr2:
        if val not in arr1:
            arr1 = np.sort(np.append(arr1,[val]))

def add_keyboard_map_2_pickles():
    '''Function to apply the process to all pickle files in the dba '''
    
    pickle_files_list = get_file_list(dataFolder, extension='.pickle')
    
    for i, pickle_file in enumerate(pickle_files_list):
        if i%20 == 0:
            print('Updating file index:', i, 'of', len(pickle_files_list))
    
        # Load content from the pickle file
        with open(pickle_file, 'rb') as file:
            file_info = pickle.load(file)
        
        # find optimal shift between detected peak frequencies and theoretical note-frequencies
        theoretical_freqs = np.arange(0,CENTS_IN_OCTAVE, 100)
        shift_cents, arr1_shft, arr2 = optimal_shift(file_info['maxima_locs_cent'], theoretical_freqs)
        theo_freqs_shifted = np.sort((theoretical_freqs - shift_cents) % CENTS_IN_OCTAVE)
        map_2_closest(theo_freqs_shifted, file_info['maxima_locs_cent'])
        
        file_info['mapped_key_freqs_cent'] = theo_freqs_shifted
        
        # cenversion from cents to hertz
        pitch_sca_fact = 4
        
        # # make sure to include one more tone after the octave
        # if theo_freqs_shifted[-1] < CENTS_IN_OCTAVE:
        #     theo_freqs_shifted = np.append(theo_freqs_shifted,[theo_freqs_shifted[0]+CENTS_IN_OCTAVE])
        maxima_locs_hz = cents_to_hz(theo_freqs_shifted, reference_frequency=reference_freq)
        
        # Define frequencies for the keys 'asdfghjkl'
        file_info['mapped_key_freqs_hz'] = maxima_locs_hz * pitch_sca_fact
        
        
        # Save extended content to the pickle file
        with open(pickle_file, 'wb') as file:
            pickle.dump(file_info, file)  
            
if __name__ == "__main__":
    add_keyboard_map_2_pickles()