#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for comparing pitch estimates 
@author: z11164
"""
import os, pickle
import numpy as np
import matplotlib.pyplot as plt
from common_tools import get_file_list
import essentia.standard as ess
import librosa


dataFolder = '../AudioCollection/CDsWithTags'

# spectrogram computation parameters
sr = 16000
H = int(sr/100) # hop size in samples 10 msec
N = 2048 # window size in samples
zero_pad = 2048 # zero-padding for STFT (only for visualization)
F_min = 55.0 # minimum frequency of interest in Hz
F_max = 1760.0 # maximum frequency of interest in Hz
plot_dur_sec = 20 # plot only for the first 30 seconds

pickle_file_list = get_file_list(dataFolder, extension='.pickle')

methods = ['pyin','crepe','makam']

for pickle_file in pickle_file_list:
    # Output image file
    jpeg_file = pickle_file.replace('.pickle','.p.jpeg')
    
    if not os.path.exists(jpeg_file):
        # Load content from the pickle file
        with open(pickle_file, 'rb') as file:
            file_info = pickle.load(file)
            
        # Get minimum and maximum pitch values
        min_f0 = F_max; # start with extremes, update in loop
        max_f0 =0
        for method in methods:
            method_min = np.min(file_info['pitch_'+method])
            method_max = np.max(file_info['pitch_'+method])
            if method_min < min_f0:
                min_f0 = method_min
            if method_max > max_f0:
                max_f0 = method_max
        # Load audio
        print(file_info['file_name'])
        audio_file_name = dataFolder+file_info['file_name']
        audio_sig = ess.MonoLoader(filename = audio_file_name, sampleRate = sr)()
        audio_dur_sec = audio_sig.shape[0]/sr
        
        # Compute spectrogram
        audio_sig_chunk = audio_sig[:int(plot_dur_sec*sr)]
        X = librosa.stft(audio_sig_chunk, n_fft=N+zero_pad, hop_length=H, win_length=N, window='hann', pad_mode='constant', center=True)
        
        amp_spec = np.abs(X)
        amp_spec[amp_spec < np.finfo(float).eps] = np.finfo(float).eps
        amp_spec_log = np.log10(amp_spec)
    
        F_coef_lin = librosa.fft_frequencies(sr=sr, n_fft=N+zero_pad)
        T_coef = librosa.frames_to_time(np.arange(X.shape[1]), sr=sr, hop_length=H)
        fig = plt.figure(figsize=(15,8))
        plt.subplot(2,1,1)
        plt.pcolormesh(T_coef, F_coef_lin, amp_spec_log, cmap='gray_r', shading='auto') #np.transpose(spktrgrm))
        plt.ylim([0, max_f0+100]) # zoom to region of actual estimates
        plt.title('Amplitude spectrogram')
        plt.ylabel('frequency(Hz)')
        plt.xlabel('time(secs)')
        colors = ['r.','g.','b.','c.']
        for c, method in zip(colors, methods):
            num_est_per_sec = file_info['pitch_'+method].shape[0]/audio_dur_sec
            num_est_plot_dur = int(plot_dur_sec * num_est_per_sec)
            t = np.linspace(0, T_coef[-1], num_est_plot_dur)
            plt.plot(t, file_info['pitch_'+method][:num_est_plot_dur],c,label=method)
        plt.legend(loc='upper right')
        plt.subplot(2,1,2)
        for c, method in zip(colors, methods):
            if 'pitch_'+method+'_conf' in file_info:
                num_est_per_sec = file_info['pitch_'+method].shape[0]/audio_dur_sec
                num_est_plot_dur = int(plot_dur_sec * num_est_per_sec)
                t = np.linspace(0, T_coef[-1], num_est_plot_dur)
                plt.plot(t, file_info['pitch_'+method+'_conf'][:num_est_plot_dur],c,label=method)
        plt.xlim([0, t[-1]])
        
        plt.savefig(jpeg_file, dpi=100)
        plt.close()

    

