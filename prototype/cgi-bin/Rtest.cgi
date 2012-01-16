#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 	Main script for testing running R-script's by uploading file 
# 	from webpage and showing immeadiate results from user.
#
#	Security issues must be solved.

import os
import sys
import string
import subprocess
import cgi 					# From this we get POST-arguments from HTML-form
import Rdump 				# Module for dumping R-scripts execution info into STDOUT
import verifyFS				# Verify cgi.FieldStorage items. Currently only runsemf81 is implemented.
import sw_fileoperations	# Some random file operation crap is here. Path building for uploaded files, etc.

import pyper 				# Import PypeR -- Python based R-script interpreter 
import pyper_runs

debug = True				# Print debugging information in STDOUT
web = True					# STDOUT is webpage

fs = cgi.FieldStorage()		# Take all arguments from POST
upfile = None				# Uploaded file from fs. In local probably some test file.

			  #############
			  ### DEBUG ###
			  #############

if debug:					
  if web:
	print "Content-Type: text/plain;charset=utf-8"
	print	
	
  for key in fs.keys():		# Print POST-arguments from cgi.FieldStorage
	if key != 'upfile':
	  print "%s = %s" % (key, fs[key].value)
	else:
	  upfile = fs[key]
	  print "%s" % upfile.filename
	  
			  ##############
			  ### /DEBUG ###
			  ##############

run_args = verifyFS.runsemf81(fs) 					# Verify cgi.FieldStorage's contents for reasonable parametres.

if run_args is -1:
  sys.exit('Give some good parametres, kthxbai.')

uniquepath = sw_fileoperations.buildpath(upfile)	# Determine and create filepath to upload to.

if uniquepath is -1:								# Could not create dir. Exiting.
  sys.exit('Could not create dir to upload file.')
  

  
run_args['infile'] = uniquepath
run_args['outfolder'] = os.path.dirname(uniquepath)

print
print
print 'Your results can be found from %s/' % (run_args['outfolder'].replace('/home/slinkola/htdocs/', 'http://slinkola.users.cs.helsinki.fi/'))

#print run_args['infile']
#print run_args['outfolder']
#print r'%s/Rout.txt' % (run_args['outfolder'])

# Run R script with passed arguments
#p = subprocess.Popen(['R', 'CMD', 'BATCH', run_args['infile'], r'%s/Rout.txt' % (run_args['outfolder'])], shell=False)
#p.wait();

if debug:
  #Rdump.runsemf81(web, runmax = 2, infile = run_args['infile'], outfolder = run_args['outfolder'])		# Dump relevant information of R-script's run.
  print

pyper_runs.runsemf81(run_args)


			  #############
			  ### DEBUG ###
			  #############

if debug:
  Rdump.runsemf81(web, runmax = 2, infile = run_args['infile'], outfolder = run_args['outfolder'])		# Dump relevant information of R-script's run.
  print
  
  #if getpass.getuser() != 'slinkola':	# Remove uploaded file if not local user.
	#try:
	  #os.remove(upfilepath)
	  #print 'Uploaded file at \'%s\' removed succesfully after R-script\'s execution' % (upfilepath)
	#except:
	  #print 'Could not remove the uploaded file'
	  
			  ##############
			  ### /DEBUG ###
			  ##############
	
	
