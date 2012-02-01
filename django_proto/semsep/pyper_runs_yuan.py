#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyper import R		# Import PypeR -- Python based R-script interpreter 
from Stemweb.local import lstrings
#import os

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
  
    if run_args is None:						# Stupid. Use properly.
        print 'No arguments given for pyper_runs_yuan.runsemf81'
        return

    # Probably could check that all running arguments are in there.
  
    r = R()										# Make instance of R.
    r.assign("iinfile", run_args['infile'])     # Assign all arguments
    r.assign("irunmax", run_args['runmax'])		
    r.assign("iitermax", run_args['itermax'])
    r("irunmax = as.numeric(irunmax)")          # Change integers into numeric
    r("iitermax = as.numeric(iitermax)")		
    
    r("source('%s/django_proto/semsep/allf81.r')" % (lstrings.project_path))
  
    print r("%s <- runf81(iinfile, iitermax, irunmax)" % (run_args['outfolder']))	# Run runsemf81 function
    
    return 
  
  
  
