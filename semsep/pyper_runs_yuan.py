#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyper import *		# Import PypeR -- Python based R-script interpreter 
import os
import saveres.py

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
        print 'No arguments given for pyper_runs_yuan.runsemf81'
        return

    # Probably could check that all running arguments are in there.
  
    r = R()										# Make instance of R.
  
    r.assign("irunmax", run_args['runmax'])		
    r("irunmax = as.numeric(irunmax)")			# Change into numeric in R
    r("irunmax")
  
    r.assign("iitermax", run_args['itermaxin'])
    r("iitermax = as.numeric(iitermax)")		# Change into numeric in R
    r("iitermax")
  
    r.assign("iinfile", run_args['infile'])		# Assign absolute path to infile
    r("iinfile")

    r("source('/Stemweb/semsep/allf81.r')")


    r("%s <- runsemf81(iinfile, iitermax, irunmax)")	# Run runsemf81 function
    #get results to python
    f81res = r.get('runf81res')
    writefile(Rres=f81res, outfolder = run_args['outfolder'])

    return 
  
  

  
	
  
