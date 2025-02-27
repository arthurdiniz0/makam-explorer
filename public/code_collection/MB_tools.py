#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 16:48:41 2024

Collection for tools using MusicBrainz API

@author: barisbozkurt
"""


from mutagen.id3 import ID3, UFID
import musicbrainzngs
import webbrowser
import requests
import time

def read_musicbrainz_id(file_path):
    try:
        audio = ID3(file_path)
        # The MusicBrainz ID is stored in the UFID frame with MusicBrainz as the owner
        mbid_frame = audio.get('UFID:http://musicbrainz.org')
        if mbid_frame:
            # Returning the MusicBrainz ID as a string
            return mbid_frame.data.decode('utf-8')
        else:
            return "No MusicBrainz ID found."
    except Exception as e:
        return f"Error reading file: {str(e)}"


def get_musicbrainz_metadata(mbid):
    try:
        # Configure the library to use the appropriate MusicBrainz server
        musicbrainzngs.set_useragent("AppName", "1.0", "YourContactInfo")  # Replace with your app's details

        # Retrieve data from MusicBrainz based on the MBID
        result = musicbrainzngs.get_recording_by_id(mbid, includes=["artists", "releases"])

        # Print all available information for the given MBID
        return result
    except musicbrainzngs.WebServiceError as exc:
        return f"MusicBrainz service error: {exc}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def fetch_musicbrainz_metadata(track_id):
    """
    Fetch metadata from MusicBrainz API for a given track ID.
    """
    url = f"https://musicbrainz.org/ws/2/recording/{track_id}"
    params = {
        "fmt": "json",  # Request JSON format
        "inc": "artists+releases"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for {track_id}: {e}")
        return None


def get_recording_tags(mbid):
    # Configure the client to access the MusicBrainz API
    musicbrainzngs.set_useragent("ExampleMusicApp", "0.1", "https://your-contact-info.com")

    try:
        # Fetch the recording details using the MusicBrainz ID
        result = musicbrainzngs.get_recording_by_id(mbid, includes=["tags"])
        recording = result["recording"]
        tags = recording.get('tag-list', [])
        
        # Extract tags if available
        if tags:
            return [tag['name'] for tag in tags]
        else:
            return "No tags found for this recording."
    except musicbrainzngs.WebServiceError as e:
        return f"MusicBrainz API error: {str(e)}"


def get_musicbrainz_track_id(album_id, disc_number, track_number, retries=5, delay=2):
    """
    Access the MusicBrainz track ID for a given album, disc, and track number, with retries and delays.
    
    :param album_id: MusicBrainz album ID (release ID).
    :param disc_number: Disc number in the album.
    :param track_number: Track number on the disc.
    :param retries: Number of retry attempts if the service is unavailable.
    :param delay: Delay in seconds between retries.
    :return: The MusicBrainz track ID or None if not found.
    """
    base_url = f"https://musicbrainz.org/ws/2/release/{album_id}"
    params = {
        "fmt": "json",  # Request JSON format
        "inc": "recordings"  # Include recordings in the response
    }
    
    for attempt in range(1, retries + 1):
        try:
            # Make a GET request to the MusicBrainz API
            response = requests.get(base_url, params=params)
            
            # Check if the response status is 503 (Service Unavailable)
            if response.status_code == 503:
                print(f"Attempt {attempt}: Service Unavailable. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue  # Retry after the delay
            
            response.raise_for_status()
            
            data = response.json()
            
            # Traverse through the tracks to find the matching disc and track number
            for medium in data.get("media", []):
                if medium.get("position") == disc_number:  # Match disc number
                    for track in medium.get("tracks", []):
                        if track.get("position") == track_number:  # Match track number
                            return track["recording"]["id"]  # Return the track's MusicBrainz ID
            
            print("Track not found for the given disc and track number.")
            return None
        
        except requests.RequestException as e:
            print(f"Attempt {attempt}: Error accessing MusicBrainz API: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Maximum retry attempts reached.")
                return None



# # Example usage
# file_path = "01. Les nuits damour.mp3"
# mbid = read_musicbrainz_id(file_path)
# print("MusicBrainz ID:", mbid)
# print('Address: https://musicbrainz.org/recording/'+mbid)

# # Uncomment line below to open a web browser to access the MB-page 
# webbrowser.open_new('https://musicbrainz.org/recording/'+mbid)

# #metadata = get_musicbrainz_metadata(mbid)
# metadata = musicbrainzngs.get_recording_by_id(mbid, includes=["artists", "releases", "tags"])

# print(metadata)

