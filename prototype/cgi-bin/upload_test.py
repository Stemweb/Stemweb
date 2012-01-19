# -*- coding: utf-8 -*-

import os

# This is mostly copypaste code from:
# http://webpython.codepoint.net/mod_python_publisher_big_file_upload
# All props to them.

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
  while True:
	chunk = f.read(chunk_size)
	if not chunk: break
	yield chunk
	
#	Uploads the given file into given path.
#
#	params:
#		upfile - File to upload. This is NOT a default python file object.
#				 Instead it's cgi.FieldStorage 'file'. That has different 
#				 properties as upfile.filename, etc.
#		dir_path - Folder for file to upload.
#
#	Returns relative file path to uploaded file on success. 
#	Returns -1 if there was no file or it was regular file.
#	Returns 0 is file already exists (this shouldn't happen,
#   since dir_path's exist-status is checked before this.)
#	or upfile couldn't be opened.

def upload(upfile = None, dir_path = r'./../htdocs/out/'):
      
  if upfile == None:					# No POST-form file-wrapper given 
	print 'No file!'
	return -1,

  upfilepath = None

  if upfile.filename:					# Test if the file was uploaded
	fname = os.path.basename(upfile.filename)	# Strip leading path from file name to avoid directory traversal attacks
	upfilepath = os.path.join(dir_path, fname)
  else:
	print 'File was empty inside form-wrapper or file didn\'t upload for some reason'
	return -1,
	
  if upfilepath is not None and os.path.exists(upfilepath):
	print 'File already exists'
	return 0
  else:
	print 'Uploading file %s...' % upfile.filename

  try:											# Upload the file
	f = open(os.path.join(dir_path, fname), 'wb', 10000)
	print 'File opened in server succesfully'
  except: 
	print 'Error in opening file to upload'
	return 0
 
  for chunk in fbuffer(upfile.file): 			# Read the file in chunks
    f.write(chunk)
  f.close()
  print 'The file "%s" was uploaded successfully' % fname
  
  os.chmod(upfilepath, 0o755)					# Give permissions

  print 
  print
  print '################### DEBUG ######################'
  print upfilepath
  f = open(upfilepath)
  for line in f.readlines():
    print line

  f.close()
  print '################### DEBUG ######################'
   
  return upfilepath
