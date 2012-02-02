#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyper import R		# Import PypeR -- Python based R-script interpreter 

import saveres
#from Stemweb import local

project_path = r'/Users/slinkola/STAM/Stemweb'

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
    print r("irunmax")
  
    r.assign("iitermax", run_args['itermaxin'])
    r("iitermax = as.numeric(iitermax)")		# Change into numeric in R
    print r("iitermax")
  
    r.assign("iinfile", run_args['infile'])		# Assign absolute path to infile
    print r("iinfile")

    print r("source('%s/semsep/allf81.r')" % (project_path))


    print r("runf81res <- runf81(iinfile, irunmax, iitermax)")	# Run runsemf81 function
    #get results to python
    f81res = r.get('runf81res')
    saveres.writefile(Rres=f81res, outfolder = run_args['outfolder'])

    return 



# Small main program to test code
run_args = dict({'itermaxin' : 10, 
                 'runmax'    : 2, 
                 'infile'    : 'test.nex', 
                 'outfolder' : '/Users/slinkola/STAM/upload/'})
runsemf81(run_args)

  
