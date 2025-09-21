#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 09:45:58 2025

During processing of the data, it was observed that some of the musicBrainz 
IDs found and embedded in the mp3-id3 tags using MusicBrainz Picard were pointing
to other recordings of the collection.

To find such problems, check_disknumbers_id3 function in this script compares 
CD-index and track index obtained two ways:
    - From file path (folder name and file name) 
    - From musicBrainz, accessing through musicBrainz ID
and returns a dictionary of mp3-file-paths and correct mbid for files that need
correction

update_metadata_mp3_pickle function updates the mp3 file (id3) and the pickle 
file (metadata) to correct the errors

Finally check_disknumbers_id3 is called again to make sure all necessary 
corrections are performed and there remains no mbid mismatch problems

@author: barisbozkurt
"""
#import os
import pandas as pd
from constants import dataFolder, musicbrainz_releaseid
from common_tools import get_file_list, update_id3_tags, update_pickle_metadata
from mutagen.easyid3 import EasyID3
#from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, USLT
from MB_tools import fetch_musicbrainz_metadata, get_musicbrainz_track_id


def check_disknumbers_id3():
    '''
    Function to check mbid mismatches in data. It has been observed that
    discnumber and tracknumber information could be used to check data consistency
    
    This function reads id3 tags placed by MusicBrainz Picard in the mp3 and compared
    with the actual file name and location of the mp3. 
    
    The files (where there is mismatch) are populated in 'correction_list' a dictionary
    mapping file-name to correct mbid

    Returns
    -------
    None. Prints mismatches list

    '''
    musicbrainz_albumid = musicbrainz_releaseid  # release id for the collection, from constants.py

    mp3_files_list = get_file_list(dataFolder, extension='.mp3')
    correction_list = {}
    for mp3_file in mp3_files_list:
        # Retrieve cd-index and track-index from file name
        CD_index = mp3_file.replace(dataFolder,'').replace('CD ','').split('/')[0]
        track_index = mp3_file.replace(dataFolder,'').replace('CD ','').split('/')[1].split('.')[0]
        
        # Retrieve cd-index and track-index from ID3 of the mp3 file
        audio = EasyID3(mp3_file)
        audio_discNo = audio["discnumber"][0].split('/')[0]
        audio_trackNo = audio["tracknumber"][0].split('/')[0]
        if len(audio_trackNo) < 2:
            audio_trackNo = '0' + audio_trackNo
        
        index_from_filename = f"{CD_index}-{track_index}"
        index_from_id3 = f"{audio_discNo}-{audio_trackNo}"

        # Detect mismatch, find mbid from disc-number and track-number from file name
        if index_from_filename != index_from_id3:
            print(f'Mismatch Mp3Filename:{index_from_filename} Mp3ID3Info:{index_from_id3}')
            
            # Retrieve mbid using disc-number and track-number obtained from file name
            discnumber = int(CD_index)
            tracknumber = int(track_index)
            track_id = get_musicbrainz_track_id(musicbrainz_albumid, discnumber, tracknumber)
            
            # if mbid found, put it in correction_list
            if track_id:
                # print(f"MusicBrainz track ID from mp3file index: {track_id}")
                correction_list[mp3_file] = track_id
            else:
                print(f"Track ID could not be found for {mp3_file}")
                correction_list[mp3_file] = -1

    return correction_list
        

def update_metadata_mp3_pickle(mp3_map):
    """
    Update ID3 tags for a dictionary mapping MP3 file names to MusicBrainz track IDs.
    Updates mp3 files and pickle files
    """
    for file_path, track_id in mp3_map.items():
        print(f"Processing {file_path} with MusicBrainz ID {track_id}")
        
        # Fetch metadata from MusicBrainz, update mp3-id3 
        metadata = fetch_musicbrainz_metadata(track_id)
        if metadata:
            update_id3_tags(file_path, metadata)
        
        # Update pickle file from info on musicbrainz
        pickle_file = file_path.replace('.mp3','.pickle')
        update_pickle_metadata(pickle_file, track_id)

#----------------------------------
# # Checking all mp3 files for mismatches between cd-track info of file name and musicBrainz
correction_list = check_disknumbers_id3()

# # Save correction list to a file: mbid_correction_list.csv
df = pd.DataFrame(list(correction_list.items()), columns=['filename', 'mbid'])
df['link'] = 'https://musicbrainz.org/recording/' + df['mbid']
df.to_csv('mbid_correction_list.csv',index=False)

# Correct ID3s of mp3 and metadata of pickle files
update_metadata_mp3_pickle(correction_list)


# re-check updated versions
correction_list_final = check_disknumbers_id3()
if len(correction_list_final) == 0:
    print('All mismatches resolved!')
else:
    print('Check out! Some mbid mismatches could not be automatically resolved')
    print(correction_list_final)
    #
    df = pd.DataFrame(list(correction_list_final.items()), columns=['filename', 'mbid'])
    df['link'] = 'https://musicbrainz.org/recording/' + df['mbid']
    df.to_csv('mbid_correction_list_remaining.csv',index=False)
    



