#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 19:04:24 2025

Script to create an archieve of files in the collection
The archieve file is named with the current date
Edit files2add to define which files will be included in the archieve

@author: barisbozkurt
"""

import zipfile
import datetime
import os, shutil
from common_tools import get_file_list

files2add = ['.pickle', '.jpeg','.csv','.py','.txt','.json']

code_files = ['readme.txt','requirements_sub.txt', 
              'common_tools.py', 'constants.py', 'create_archieve.py', 'correct_data.py',
              'extract_pitch.py', 'tuning_analysis.py','MB_tools.py',
              'region_artists.json','create_region_artists.py',
              'retrieveMetadata4allFiles.py']

# Retrieve file list
dataFolder = '../AudioCollection/CDsWithTags'

# Copy code to a subfolder
codeFolder = dataFolder + '/code'
if not os.path.exists(codeFolder):
    os.mkdir(codeFolder)
for file_name in code_files:
    if os.path.isfile(file_name):
        shutil.copy(file_name, codeFolder)
        print(f"Copied: {file_name}")
    else:
        print(f"File not found: {file_name}")

file_list = []
for file_extension in files2add:
    file_list += get_file_list(dataFolder, extension=file_extension)

# Generate the zip file name using the current date
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
zip_file_name = f"CairoCong1932_features_plots_{current_date}.zip"

# Create a zip file and add the files
with zipfile.ZipFile(zip_file_name, 'w') as zipf:
    for index, file in enumerate(file_list, start=1):
        if index % 50 == 1:
            print(f"Adding file {index}/{len(file_list)}")

        if os.path.exists(file):  # Check if the file exists before adding
            # Generate subfolder name based on the file name (without extension)
            subfolder_name = os.path.dirname(file.replace(dataFolder,'')).split('/')[-1]
            # Add file to the zip archive under the subfolder
            arcname = os.path.join(subfolder_name, os.path.basename(file))
            zipf.write(file, arcname=arcname)
        else:
            print(f"Warning: {file} does not exist and will not be added.")

print(f"Files successfully packed into {zip_file_name}")
