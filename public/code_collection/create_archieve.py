#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 19:04:24 2025

Script to create an archieve of files in the collection with a specific extension
The archieve file is named with the current date


@author: barisbozkurt
"""

import zipfile
import datetime
import os
from common_tools import get_file_list

file_extension = '.pickle'

# Retrieve file list
dataFolder = '../AudioCollection/CDsWithTags'

file_list = get_file_list(dataFolder, extension=file_extension)

# Generate the zip file name using the current date
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
zip_file_name = f"backup_{current_date}_{file_extension}.zip"

# Create a zip file and add the files
with zipfile.ZipFile(zip_file_name, 'w') as zipf:
    for index, file in enumerate(file_list, start=1):
        if index % 50 == 1:
            print(f"Adding file {index}/{len(file_list)}")

        if os.path.exists(file):  # Check if the file exists before adding
            # Generate subfolder name based on the file name (without extension)
            subfolder_name = os.path.dirname(file).split('/')[-1]
            # Add file to the zip archive under the subfolder
            arcname = os.path.join(subfolder_name, os.path.basename(file))
            zipf.write(file, arcname=arcname)
        else:
            print(f"Warning: {file} does not exist and will not be added.")

print(f"Files successfully packed into {zip_file_name}")
