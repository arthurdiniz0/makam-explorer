#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:35:06 2024

Script for computing pitch features from audio files

Outputs stored in pickle files in the same folder as the audio files.

Various pitch extraction methods (stored in list: methods) are used 
and series computed using these methods are all stored.

Features:
    file_info['pitch_*'] 
    file_info['pitch_hist_values_*']
    file_info['pitch_hist_edges']
(*: pitch extraction method)

    
@author: barisbozkurt
"""
import os
import numpy as np
#import matplotlib.pyplot as plt
import librosa
import crepe
#import torch, pesto # dropped after observing its quality not surpessing others
import essentia.standard as ess
import pickle

from constants import pitch_extraction_methods, pitch_params, CENTS_IN_OCTAVE, num_notes_in_octave, num_octaves_in_hist, reference_freq, dataFolder
from MB_tools import read_musicbrainz_id
from common_tools import get_file_list, plot_hist, compute_maxima_locs_from_hist, moving_average_3_point, hz_to_cent_array
from predominantmelodymakam.predominantmelodymakam import PredominantMelodyMakam


makamPitchExtractor = PredominantMelodyMakam(hop_size=int(pitch_params['H']*2.758), # scaling required to match number of estimates with other methods: pyin and crepe
                                             frame_size=pitch_params['N'])


def get_pitch_series(mp3_file, audio_sig, params, method='pyin'):
    if method == 'pyin':
        f0, voiced_flag, conf = librosa.pyin(audio_sig,sr=pitch_params['sr'],
                                             hop_length=pitch_params['H'],
                                             fmin=pitch_params['F_min'],
                                             fmax=pitch_params['F_max'])
    elif method == 'crepe':
        t_crepe, f0, conf, act_crepe = crepe.predict(audio_sig, pitch_params['sr'], viterbi=True)
    # elif method == 'pesto':
    #     t_pesto, f0, conf, act_pesto = pesto.predict(torch.from_numpy(audio_sig), params['sr'])
    #     f0 = f0.numpy() # f0.cpu().detach().numpy()
    #     conf = conf.numpy() # conf.cpu().detach().numpy()
    elif method == 'makam':
        results = makamPitchExtractor.run(mp3_file)
        p = np.array(results['pitch'])
        f0 = p[:,1]
        conf = p[:,2]/np.max(p[:,2])
    else:
        print('Unknown pitch extraction method')
        f0 = np.array([]); conf = np.array([])
    return f0, conf

def run_pitch_extract_on_collection(dataFolder, methods, overwrite_methods):

    mp3_file_list = get_file_list(dataFolder)
    num_files = len(mp3_file_list)
    
    pickle_file_list = []
    for i, mp3_file in enumerate(mp3_file_list):
        feature_extraction_executed = False
        # Specify the filename for the pickle file
        pickle_file = '.'.join(mp3_file.split('.')[:-1])+'.pickle' # replace file extension with pickle
        pickle_file_list.append(pickle_file)
        # Run analysis if analysis outputs file does not exist
        if not os.path.exists(pickle_file):
            print(i, '/', num_files, mp3_file.split(dataFolder)[-1])
            file_info = {}
            file_info['file_name'] = mp3_file.split(dataFolder)[-1]
            file_info['mbid'] = read_musicbrainz_id(mp3_file)
            audio_sig = ess.MonoLoader(filename = mp3_file, sampleRate = pitch_params['sr'])()
            for method in methods:
                print('Extracting pitch with', method)
                pitch, conf = get_pitch_series(mp3_file, audio_sig, pitch_params, method)
                file_info['pitch_'+method] = pitch
                file_info['pitch_'+method+'_conf'] = conf
                feature_extraction_executed = True
    
        else: # if pickle file exist check existance of feature and run extractor if not exists or forced to re-compute
            # Load content from the pickle file
            with open(pickle_file, 'rb') as file:
                file_info = pickle.load(file)
            
            for method in methods:
                # Run computation if re-computation is specified or method has not been previously used
                if (method in overwrite_methods) or ('pitch_'+method not in file_info):
                    print('Extracting pitch with', method)
                    print(i, '/', num_files, mp3_file.split(dataFolder)[-1])
                    audio_sig = ess.MonoLoader(filename = mp3_file, sampleRate = pitch_params['sr'])()
                    pitch, conf = get_pitch_series(mp3_file, audio_sig, pitch_params, method)
                    file_info['pitch_'+method] = pitch
                    file_info['pitch_'+method+'_conf'] = conf
                    feature_extraction_executed = True
        
        if feature_extraction_executed:
            print('len_pyin:',file_info['pitch_pyin'].shape[0], 
                  'len_crepe:',file_info['pitch_crepe'].shape[0], 
                  'len_makam:', file_info['pitch_makam'].shape[0])
            # Save the dictionary to a pickle file
            with open(pickle_file, 'wb') as file:
                pickle.dump(file_info, file)  
    return pickle_file_list 

def compute_pitch_histograms(pickle_file_list, methods, hist_bins, bin_step_cents, overWriteImages=False):
    '''
    Compute pitch histogram for each of the file in pickle_file_list

    Parameters
    ----------
    pickle_file_list : list
        Pickle files list.
    methods : list
        List of pitch extraction method names.
    hist_bins : numpy.array
        Bins used to compute the histogram.
    bin_step_cents : float
        Histogram bin size in cents.
    overWriteImages : bool, optional
        Flag to control re-creation of files containing plots. The default is False.

    Returns
    -------
    None. Updates pickle files (adds histograms to dictionary content), recreates plot files

    '''
    for i, pickle_file in enumerate(pickle_file_list):
        # Output image file
        jpeg_file = pickle_file.replace('.pickle','.h.jpeg')
        
        if not os.path.exists(jpeg_file) or overWriteImages:
        
            # Load content from the pickle file
            with open(pickle_file, 'rb') as file:
                file_info = pickle.load(file)
            
            remove_frame = find_pitch_frames2drop(pickle_file, methods, pitch_params, conf_threshold=0.4)
            
            average_hist = np.zeros((hist_bins.shape[0]-1, ))
            for method in methods:
                pitchSeriesHz = file_info['pitch_'+method][:remove_frame.size]
                pitchSeriesHz[remove_frame] = np.nan
                pitchSeriesCents = hz_to_cent_array(pitchSeriesHz, reference_freq)
                pitchSeriesCents = pitchSeriesCents[~np.isnan(pitchSeriesCents)] # dropping nan values
                
                values, edges = np.histogram(pitchSeriesCents, bins = hist_bins)
                edge_mid_points = (edges[:-1] + edges[1:]) / 2
                file_info['pitch_hist_values_'+method] = values
                file_info['pitch_hist_edges'] = edge_mid_points
                
                average_hist += values
            
            average_hist /= len(methods)
            file_info['pitch_hist_values_mean'] = moving_average_3_point(average_hist)
            file_info['maxima_locs_cent'] = compute_maxima_locs_from_hist(file_info)
            file_info['intervals'] = np.diff(file_info['maxima_locs_cent'])
                
            # Save the dictionary to a pickle file
            with open(pickle_file, 'wb') as file:
                pickle.dump(file_info, file)
            
            # Plot the histogram in a jpeg file
            plot_hist(pickle_file, jpeg_file, methods)
            
            if i % 20 == 0 and i != 0:
                print('Processed', i, 'files computing histograms')
    
def find_pitch_frames2drop(pickle_file, methods, pitch_params, conf_threshold=0.4):
    '''
    Finds which frames should be dropped via merging decisions:
        drop if confidence is lower than threshold
        drop if energy is lower than threshold
        drop if more than one of the methods fail to detect pitch    

    Parameters
    ----------
    pickle_file : str
        Path to pickle file.
    methods : list
        List of pitch extraction method names.
    pitch_params : dict
        Pitch computation parameters.
    conf_threshold : float, optional
        Pitch confidence threshold assuming conf in range 0-1. The default is 0.4.

    Returns
    -------
    remove_frame : bool array
        Boolean index array for frames to remove. True: remove-frame, False=keep frame.

    '''
    
    # Confidence keys to use for decision
    conf_series_key = 'pitch_crepe_conf'
    
    # Load content from the pickle file
    with open(pickle_file, 'rb') as file:
        file_info = pickle.load(file)
    # Compute energy
    audio_sig = ess.MonoLoader(filename = pickle_file.replace('.pickle','.mp3'), sampleRate = pitch_params['sr'])()
    NRG = []
    for frame in ess.FrameGenerator(audio_sig, frameSize=pitch_params['N'], 
                                    hopSize=pitch_params['H'], startFromZero=False):
        NRG.append(ess.Energy()(frame))
    NRG = np.array(NRG)
    
    # match lens
    min_len = min(NRG.shape[0], file_info[conf_series_key].shape[0])
    
    # Silence/noise decision    
    low_conf_frame = file_info[conf_series_key][:min_len] < (np.max(file_info[conf_series_key]) * conf_threshold)
    
    # Apply energy threshold
    #   a dynamic range is set in log-energy as (mean-delta, mean+delta) where
    #   delta is computed as max - mean and all values below mean-delta is considered as low energy
    log_NRG = np.log(NRG+np.finfo(float).eps)
    log_NRG_threshold = np.mean(log_NRG) - (np.max(log_NRG)-np.mean(log_NRG))
    low_energy_frame = log_NRG[:min_len] < log_NRG_threshold

    # find indexes with more than one nan values in pitch estimates to also set the other nan    
    nan_frames = np.zeros((min_len, len(methods)))
    for i, method in enumerate(methods):
        nan_frames[:, i] = np.isnan(file_info['pitch_'+method])[:min_len]
    nan_frames = np.sum(nan_frames, axis=1) >= 2
    
    remove_frame = np.logical_or(low_conf_frame, low_energy_frame)
    remove_frame = np.logical_or(remove_frame, nan_frames)
    
    return remove_frame
    
    # #Plot to check decision
    # plt.figure(figsize=(10,8))
    # plt.subplot(2,1,1)
    # colors = ['c','g','b']
    # pitch_series_keys = [key.replace('_conf','') for key in file_info.keys() if 'conf' in key]
    # for c, pitch_key in zip(colors, pitch_series_keys):
    #     plt.plot(file_info[pitch_key], c, label=pitch_key)
    # plt.legend(loc='upper right')
    # plt.subplot(2,1,2)
    
    # plt.plot(file_info[conf_series_key],'k')
    # plt.plot(NRG/np.max(NRG),'b')
    # plt.plot(remove_frame,'r', linewidth=2.5)
    # plt.show()

    


# Run pitch extraction using the listed methods 
overwrite_methods = [] #overwrite_methods = ['makam'] # re-compute even if exists, keep empty if re-computation is not needed
pickle_file_list = run_pitch_extract_on_collection(dataFolder, pitch_extraction_methods, overwrite_methods)

# Computing pitch histograms
bin_step_cents = CENTS_IN_OCTAVE / num_notes_in_octave
hist_bins = np.arange(-bin_step_cents/2, 
                      CENTS_IN_OCTAVE*num_octaves_in_hist, bin_step_cents)

compute_pitch_histograms(pickle_file_list, pitch_extraction_methods, hist_bins, bin_step_cents, overWriteImages=True)

# pickle_file_list = get_file_list(dataFolder, extension='.pickle')
# filter_merge_pitch_series(pickle_file_list[0], pitch_params)
