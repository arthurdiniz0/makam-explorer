This folder contains Python code written/used to retrieve metadata from musicBrainz and to extract features from the audio files. All metadata accessed and features computed are stored in pickle files. 

requirements_sub.txt contains some of the library versions

In case of an update on musicBrainz, you can call the following scripts to retrieve metadata and tags from musicBrainz and update the pickle files.

1)Run common_tools.py which in the main function would run:
common_tools/update_after_tag_edit() that would read tags from musicbrainz and update pickle files.
This function will also update the csv files which contain tables of all metadata.
To update only for a subset define querySubStr and use. If kept empty, all files will be updated.

2) Run extract_pitch.py which in the main function would call run_extractor that computes pitch series (skipped if pitch series already exist) and pitch histograms. If tonic_cents available, extracts tonic frequency and creates additional histograms where tonic is set to 0 cents. 

3) Run create_archieve.py save all files of the dataset in a zip package with current date specified in the file name.


The first version of the pickle files are created using
extract_pitch/run_pitch_extract_on_collection
which requires the audio files not shared with this dataset but accessible from:
	https://archive.org/details/13.PsaumeDeLaTristesse 
other functions firt read the pickle file and then update its content.

MusicBrainz release page:
	https://musicbrainz.org/release/25d66aec-1463-4a0b-a331-d3bbe587e71c



