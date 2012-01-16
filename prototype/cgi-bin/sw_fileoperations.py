#!/usr/bin/env python
# -*- coding: utf-8 -*-

#	Some file operations and random stuff in here.
#	Refactor to some other places when relevant.

import os
import string
import random
import upload_test	# File upload module. Needs tweaking to ensure safety.

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

#	Builds (semi)unique path for uploaded file.
#	
#	Currently all builded paths have prefix ./../htdocs/out/
#	and are then concatenaded with uploaded file's name, '.'
#	and random string created with id_generator.
#
#	Also handles 
#
#	params:
#		upfile - Uploaded file. This is NOT a default python file object.
#				 Instead it's cgi.FieldStorage 'file'. That has different 
 #				 properties as upfile.filename, etc.
#
#	Returns path to upfile after it has been uploaded to it's builded
#	unique path. This is relative path to file in harddrive.
def buildpath(upfile = None): 
  
  if os.path.exists(r'/home/slinkola/htdocs/out/'):		# Debug code to keep foldersize relevantly low 
	dir_mb = dir_size(r'/home/slinkola/htdocs/out/')	# while developing software.
	print '/out/ size %s mb' % (dir_mb)
	#if dir_mb > 100:		  
	  #os.rmdir(r'./../htdocs/out/', 0o777)		
  
  if upfile is None:									# If no upfile use default. 
	upfile = r'/home/slinkola/htdocs/r-files/test.nex'
	fname = os.path.basename(upfile)
  else:
	fname = os.path.basename(upfile.filename)			# Strip possible other information from filename.
  
  uniquepath = r'/home/slinkola/htdocs/out/%s.%s' % (fname, id_generator())	# Build semiunique dir.
  
  if not os.path.exists(uniquepath):								# Create dir if it doesn't exist.
	try:															# (It really shouldn't)
	  os.mkdir(uniquepath, 0o777)									
	except:
	  print 'Couldn\'t create dir %s' % (uniquepath)
	  return -1

  os.chmod(uniquepath, 0o777)										# You seem to need to give permissions again.
  upfilepath = upload_test.upload(upfile, dir_path = uniquepath)	# Upload the file to created path.
  os.chmod(uniquepath, 0o755)										# Aaand take them away.
  
  return upfilepath
  
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
	for file in files:
	  filename = os.path.join(path, file)
	  folder_size += os.path.getsize(filename)
  
  return (folder_size/(1024*1024.0))