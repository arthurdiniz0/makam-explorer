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
import librosa
import crepe
import essentia.standard as ess
import pickle

from constants import pitch_extraction_methods, pitch_params, CENTS_IN_OCTAVE, num_notes_in_octave, num_octaves_in_hist, reference_freq, dataFolder
from MB_tools import read_musicbrainz_id
from common_tools import get_file_list, plot_hist, compute_maxima_locs_from_hist, moving_average_3_point, hz_to_cent_array, convert_tags_to_dict, warp_hist_in_1_octave, save_allMetadata_to_file
from predominantmelodymakam.predominantmelodymakam import PredominantMelodyMakam


makamPitchExtractor = PredominantMelodyMakam(hop_size=int(pitch_params['H']*2.758), # scaling required to match number of estimates with other methods: pyin and crepe
                                             frame_size=pitch_params['N'])


def get_pitch_series(mp3_file, audio_sig, params, method='pyin'):
    '''
    Runs pitch extraction on audio file

    Parameters
    ----------
    mp3_file : str
        Audio file path.
    audio_sig : numpy.array
        Audio signal.
    params : dict
        Analysis parameters.
    method : str, optional
        Name of the pitch extraction methos. The default is 'pyin'.

    Returns
    -------
    f0 : numpy.array
        Pitch series.
    conf : numpy.array
        Confidence series.

    '''
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
    '''
    Runs pitch extraction on all files of the collection

    Parameters
    ----------
    dataFolder : str
        Path to main data folder.
    methods : list of str
        Names of methods used for pitch extraction.
    overwrite_methods : list of str
        List of methods for which extraction is forced to perform.
        If overwrite_methods is empty and output exists, extraction is skipped. 

    Returns
    -------
    pickle_file_list : list of str
        List of pickle file paths.

    '''

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
            # print log of series length for sanity check
            print('len_pyin:',file_info['pitch_pyin'].shape[0], 
                  'len_crepe:',file_info['pitch_crepe'].shape[0], 
                  'len_makam:', file_info['pitch_makam'].shape[0])
            # Save the dictionary to a pickle file
            with open(pickle_file, 'wb') as file:
                pickle.dump(file_info, file)  
    return pickle_file_list 

def compute_pitch_histograms(pickle_file_list, methods, hist_bins, 
                             bin_step_cents, overWriteImages=False, querySubStr=[]):
    '''
    Compute pitch histogram for each of the file in pickle_file_list
    If tonic_cents available, extracts tonic frequency and creates additional 
    histograms where tonic is set to 0 cents

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
        It also serves as a flag to re-compute the histograms
    querySubStr: list of str
        Sub-strings to be searched in file name to select files to update 
        Example: querySubStr=["CD 13/05.","CD 13/06.","CD 13/07."] would result 
        in updating only 3 files
        Using empty list, all files are processed/updated


    Returns
    -------
    None. Updates pickle files (adds histograms to dictionary content), recreates plot files

    '''
    for i, pickle_file in enumerate(pickle_file_list):
        # Output image file
        jpeg_file = pickle_file.replace('.pickle','.h.jpeg')
        
        if not os.path.exists(jpeg_file) or overWriteImages:
            update_file = True

            # If querySubStr is not empty, use queries to decide if file will be updated
            if querySubStr:
                update_file = False
            for subStr in querySubStr:
                if subStr in pickle_file:
                    update_file = True
            if update_file:
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
                file_info['oct_warped_hist_mean'] = warp_hist_in_1_octave(file_info['pitch_hist_values_mean'], num_notes_in_octave)
                
                # if tonic_secs available in tags, then compute tonic and create additional histograms
                recording_tags_dict = convert_tags_to_dict(file_info['mb_tags'])
                if 'tonic_secs' in recording_tags_dict:
                    tonic_pitch_hz, tonic_pitch_cents = extract_tonic_from_tags(file_info, recording_tags_dict['tonic_secs'])
                    file_info['tonic_pitch_hz'] = tonic_pitch_hz
                    file_info['tonic_pitch_cents'] = tonic_pitch_cents
                
                    # find index of pitch histogram that corresponds to the tonic
                    ref_0_cents_ind = np.argmin(np.abs(file_info['pitch_hist_edges']-file_info['tonic_pitch_cents']))
                    file_info['oct_warped_hist_mean_wrt_tonic'] = warp_hist_in_1_octave(file_info['pitch_hist_values_mean'], num_notes_in_octave, ref_0_cents_ind)
                    file_info['tonic_pitch_hist_ind'] = ref_0_cents_ind
                    # print log
                    print('Pickle and hist-plot updated with tonic info:', ''.join(pickle_file.split('/')[-1].split('.')[:-1]))
    
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
    

def extract_tonic_from_tags(file_info, tonic_secs):
    '''
    Extract tonic frequency using segmentation information

    Parameters
    ----------
    file_info : dict
        Dictionary containing all features of a file.
    tonic_secs : str
        Tonic segmentation including start and stop in seconds.

    Returns
    -------
    tonic_pitch_hz : float
        Tonic pitch in hertz.
    tonic_pitch_cents : float
        Tonic pitch in cents with respect to ref_freq (440Hz), 
        which is then warped to 0-1200 range.

    '''
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
    ref_freq = reference_freq * 4 # 220 Hz
    while (len(pitches_tonic_region[pitches_tonic_region > ref_freq]) > 0):
        pitches_tonic_region[pitches_tonic_region > ref_freq] /= 2
    
    while (len(pitches_tonic_region[pitches_tonic_region < ref_freq/2]) > 0):
        pitches_tonic_region[pitches_tonic_region < ref_freq/2] *= 2
    
    # Compute mean of the middle (1/3) part of the sorted array
    sorted_vals = np.sort(pitches_tonic_region)
    start = len(sorted_vals) // 3; end = 2 * start
    tonic_pitch_hz = np.mean(sorted_vals[start:end])
    tonic_pitch_cents = np.log2(tonic_pitch_hz / ref_freq) * CENTS_IN_OCTAVE
    while tonic_pitch_cents < 0:
        tonic_pitch_cents += CENTS_IN_OCTAVE
    while tonic_pitch_cents > CENTS_IN_OCTAVE:
        tonic_pitch_cents -= CENTS_IN_OCTAVE
    
    # find closest peak in histogram and match to that value if with-in close proximity
    closest_maxima_ind = np.argmin(np.abs(file_info['maxima_locs_cent']-tonic_pitch_cents))
    delta_cents = 1.5*CENTS_IN_OCTAVE/num_notes_in_octave # threshold for closeness
    tonic_candidate_cents = file_info['maxima_locs_cent'][closest_maxima_ind]
    delta_tonic_cents = tonic_candidate_cents - tonic_pitch_cents
    if abs(delta_tonic_cents) <= delta_cents:
        tonic_pitch_hz *= (2 ** (delta_tonic_cents / 1200))
        tonic_pitch_cents = tonic_candidate_cents
    
    
    return tonic_pitch_hz, tonic_pitch_cents    

def run_extractor(overWriteImages=False, querySubStr=[]):
    '''
    Runs pitch extraction and histogram computation for all or selected group of files
    with all extractors or a sub-set
    
    overWriteImages : bool, optional
        Flag to control re-creation of files containing plots. The default is False.
        It also serves as a flag to re-compute the histograms
    querySubStr: list of str
        Sub-strings to be searched in file name to select files to update 
        Example: querySubStr=["CD 13/05.","CD 13/06.","CD 13/07."] would result 
        in updating only 3 files
        Using empty list, all files are processed/updated


    '''
    # Run pitch extraction using the listed methods 
    overwrite_methods = [] #overwrite_methods = ['makam'] # re-compute even if exists, keep empty if re-computation is not needed
    pickle_file_list = run_pitch_extract_on_collection(dataFolder, pitch_extraction_methods, overwrite_methods)
    
    # Computing pitch histograms
    bin_step_cents = CENTS_IN_OCTAVE / num_notes_in_octave
    hist_bins = np.arange(-bin_step_cents/2, 
                          CENTS_IN_OCTAVE*num_octaves_in_hist, bin_step_cents)
    
    # querySubStr = [] # to process all files
    compute_pitch_histograms(pickle_file_list, pitch_extraction_methods, hist_bins, bin_step_cents, overWriteImages=overWriteImages, querySubStr=querySubStr)
    
    # pickle_file_list = get_file_list(dataFolder, extension='.pickle')
    # filter_merge_pitch_series(pickle_file_list[0], pitch_params)

if __name__ == "__main__":
    # Run main if there are updates in tonic labels (tonic_secs in tags)
    #  this will update the pickle file to include tonic aligned pitch histogram
    files2ReProcessSubStr = []
    run_extractor(overWriteImages=True, querySubStr=files2ReProcessSubStr)
    save_allMetadata_to_file()
