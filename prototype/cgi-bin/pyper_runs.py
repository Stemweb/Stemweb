#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyper import *		# Import PypeR -- Python based R-script interpreter 
import os

#	Execute runsemf81.r with given arguments
#
#	params:
#		run_args -  dictionary containing following
#					key-value pairs:
#					'runmax' 	- int > 0
#					'itermaxin' - int > 0
#					'inputfile' - path to .nex file used to run function
#					'outfolder' - path to desirable output folder 
#
def runsemf81(run_args = None):
  
  if run_args is None:							# Stupid. Use properly.
	print 'No arguments given for pyper_runs.runsemf81'
	return
	
  # Probably could check that all running arguments are in there.
  
  r = R()										# Make instance of R.
  
  r.assign("irunmax", run_args['runmax'])		
  r("irunmax = as.numeric(irunmax)")			# Change into numeric in R
  print r("irunmax")
  
  r.assign("iitermaxin", run_args['itermaxin'])
  r("iitermaxin = as.numeric(iitermaxin)")		# Change into numeric in R
  print r("iitermaxin")
  
  r.assign("iinfile", run_args['infile'])		# Assign absolute path to infile
  print r("iinfile")
  r.assign("ioutfolder", run_args['outfolder'])	# Assign absolute path to outfolder
  print r("ioutfolder")
  
  r("source('/home/slinkola/htdocs/r-files/runsemf81.r')")
  
  print r("runsemf81(iinfile, ioutfolder, irunmax, iitermaxin)")	# Run runsemf81 function
	
  return
  
  
	
  
	
  
