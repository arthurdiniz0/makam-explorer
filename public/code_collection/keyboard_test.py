#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:11:05 2024

@author: z11164
"""

import numpy as np
import sounddevice as sd
from pynput import keyboard
import pickle
from scipy.signal.windows import tukey

from constants import pitch_params


dataFolder = '../AudioCollection/CDsWithTags'

pickle_file = dataFolder + '/CD 13/18. Mesut Cemil bey - Suite.pickle'
# Load content from the pickle file
with open(pickle_file, 'rb') as file:
    file_info = pickle.load(file)


# cenversion from cents to hertz
sr = pitch_params['sr']
dur_sca_fact = 1

# make sure to include one more tone after the octave
frequencies = file_info['mapped_key_freqs_hz']
if frequencies[-1] < (frequencies[0]*2):
    frequencies = np.append(frequencies,[frequencies[0]*2])

# Sample rate and duration
sample_rate = 16000
duration = 0.7  # seconds

def generate_tone(frequency, duration, sample_rate):
    """Generate a sine wave tone at the specified frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)  # Sine wave
    return tone * tukey(len(tone), 0.2)

def play_tone(frequency):
    """Play a tone of a given frequency."""
    tone = generate_tone(frequency, duration, sample_rate)
    sd.play(tone, sample_rate)
    sd.wait()  # Wait until the sound finishes playing

# Map keys to corresponding frequencies
key_to_frequency = {k:f for k,f in zip('sedrfgyhujikl',frequencies)}

def on_press(key):
    """Handle key press events."""
    try:
        if key.char == 'q':  # Exit when 'q' is pressed
            return False
        elif key.char in key_to_frequency:
            frequency = key_to_frequency[key.char]
            play_tone(frequency)
    except AttributeError:
        pass  # Handle special keys like shift or alt gracefully

# Set up listener for keyboard events
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
