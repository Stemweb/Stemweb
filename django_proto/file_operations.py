#!/usr/bin/env python
# -*- coding: utf-8 -*-

#	Some file operations and random stuff in here.
#	Refactor to some other places when relevant.

import os
import string
import random
from Stemweb import local

# Locally relevant default path for uploaded files. 
default_upload_path = local.lstrings.default_upload_path

# 	Semiunique ID generator -- copypaste code.
#
#	Generates random string to be added for example
#	to output folders of R-script's output.
#
#	Source:
# 	http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
#
#	params:
#		size - length of the random string. Default 8.
#		chars - set of chars from which the string is created
#
#	Returns created string
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

#	Builds unique path for uploaded file.
#	
#	Builds unique path for uploaded file with prefix 
#   as mentioned in default_upload_path
#
#	params:
#		upfile - Uploaded file. This is NOT a default python file object.
#				 Instead it's djangos 'UploadedFileInMemory'-object.
#      file_id - ID of the db-table Input_files' entry
#
#	Returns path to upfile after it has been uploaded to it's builded
#	unique path. This is absolute path to file in harddrive.
def build_filepath(upfile, file_id): 
    
#    if os.path.exists(default_upload_path):		# Debug code to keep foldersize relevantly low 
#        dir_mb = dir_size(default_upload_path)	# while developing software.
#        print '%s size %s mb' % (default_upload_path, dir_mb)
#        if dir_mb > 100:		  
#            os.rmdir(default_upload_path, 0o777)		
      
    fname = os.path.basename(upfile)			# Strip possible other information from filename.    
    uniquepath = os.path.join(default_upload_path, fname)         
    if not os.path.exists(uniquepath):		        # Create dir if it doesn't exist.
        try:
            os.mkdir(uniquepath)									
        except:
            print 'Couldn\'t create dir %s' % (uniquepath)
            return -1
        
    uniquepath = os.path.join(uniquepath, '%s' % (file_id))          
    if not os.path.exists(uniquepath):                # Create dir if it doesn't exist.
        try:                                          # (It really shouldn't)
            os.mkdir(uniquepath)                                    
        except:
            print 'Couldn\'t create dir %s' % (uniquepath)
            return -1

    return uniquepath

#    Builds unique path for run's result folder.
#
#    params:
#       runfile - Absolute path to file to use as input_file
#                 for a run.
#        run_id - ID of the R_runs db-table's entry
# 
#    Returns path to run's storage folder if it has been
#    succesfully created. Otherwise returns -1
def build_runpath(runfile, run_id): 
    path = os.path.dirname(runfile)           
    uniquepath = os.path.join(path, '%s' % (run_id))                  
    if not os.path.exists(uniquepath):                # Create dir if it doesn't exist.
        try:                                          # (It really shouldn't)
            os.mkdir(uniquepath)                                    
        except:
            print 'Couldn\'t create dir %s' % (uniquepath)
            return -1

    return uniquepath  
  
#	Calculate size of given dir.
#
#	params:
#		dir_path - relative or absolute path to dir
#
#	Returns size of dir and it's childs in Mb.
def dir_size(dir_path):
    folder = dir_path
    folder_size = 0
    for (path, dirs, files) in os.walk(folder):
        for f in files:
            filename = os.path.join(path, f)
            folder_size += os.path.getsize(filename)
  
    return (folder_size/(1024*1024.0))
  
def handle_uploaded_file(f, fpath):
    destination = open('%s/%s' % (fpath, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return destination