#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 11:37:54 2025

This script creates the region-artist map and saves in a file

@author: barisbozkurt
"""
import json

region_artists = {
    'Egypt':["Darwîsh Al-Harîrî",
             "Darwîsh Muhammad al-Harîrî",
             "Aziz 'Uthmân",
             "Dâwûd Khudr Husnî",
             "‘Abduh al-Ḥāmūlī",
             "Muhammad al-Bahr",
             "Muhammad Awad Al-Arabî",
             "Ensemble Baladî",
             "Les Bédouins du Fayyûm",
             "Taha Abû Mandûr",
             "Taha Abû Mandûr et son ensemble de hautbois et de tambours",
             "Annûsa Al-Misriyya",
             "Mustafa Fahreddin Dede",
             "Takiyya Mawlawiyya du Caire",
             "La Confrérie Laythiyya",
             "Umm Ibrâhîm Al-Mahdiyya",
             "Fâtima Al-Shâmiyya",
             "Mîkhâ'îl Jirjis al-Batânûnî"],
    'Iraq':["Ensemble de Muhammad Al-Qubbbânjî",
            "Azzûrî Hârûn Al-'Awwâd"],
    'Syria':["Fawzî al-Qaltaqjî"],
    'Turkey': ['Mesut Cemil Bey'],
    'Algeria':["L'ensemble d'Al-'Arabî Ben Sârî"],
    'Maroc':["L'ensemble de 'Umar Fâ'id Al-Ju'aydî"],
    'Tunisia':["L'ensemble de Muhammad Ghânim",
               "Khumayyis Tarnân"],
    }

# File name to save the JSON data
json_file_name = "region_artists.json"

# Save the dictionary to a JSON file
with open(json_file_name, 'w') as json_file:
    json.dump(region_artists, json_file, indent=4)
    
# Read the JSON file into a dictionary
# with open(json_file_name, 'r') as json_file:
#     region_artists = json.load(json_file)