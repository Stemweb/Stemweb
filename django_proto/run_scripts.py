#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from pyper import *		# Import PypeR -- Python based R-script interpreter 
from rpy2 import robjects
import saveres
import os
import subprocess

from Stemweb.algorithms.rhm import binarysankoff

#	Execute f81.r with given arguments
#
#	params:
#		run_args -  dictionary containing following
#					key-value pairs:
#					'runmax' 	- int > 0
#					'itermaxin' - int > 0
#					'inputfile' - path to .nex file used to run function
#					'outfolder' - path to desirable output folder 
#
def f81(run_args = None):

    if run_args is None:                            # Stupid. Use properly.
        print 'No arguments given for pyper_runs_yuan.f81'
        return

    # Probably could check that all running arguments are in there.
  
    R = robjects.r                                  # Singleton instance of R
    source = r'%s/algorithms/semsep/allf81.r' % (project_path)
    R.source(source)                            
    
    runf81 = R['runf81']                            # Run script
    f81res = runf81(run_args['infile'],             # Get results to python
                    run_args['runmax'],
                    run_args['itermaxin'])
    
                                                    # Save results
    saveres.writefile(Rres=f81res, outfolder = run_args['outfolder'])

    return 1

def rhm_test(run_args = None):
    
    if run_args is None:
        run_args = dict()
        run_args['infolder'] = os.path.join(project_path, 'algorithms', 'rhm', 'test')
        run_args['outfolder'] = os.path.join(project_path, 'algorithms', 'rhm', 'res')
        run_args['itermaxin'] = 250
        run_args['strap'] = 1
        
    if not os.path.exists(run_args['outfolder']):
        os.mkdir(run_args['outfolder'])
    
    rhm_path = os.path.join(project_path, 'algorithms', 'rhm', 'rhmrun.sh')
    try:
        #subprocess.call(rhm_path)
        binarysankoff.main(run_args)
    except:
        log_path = os.path.join(os.path.dirname(rhm_path),'log')
        log_file = open(log_path)
        log_file.write('Could not run script in %s' % (rhm_path))
        log_file.close()
        

# Small main program to test code
def main():
    if not os.path.exists('temp'):
        os.mkdir('temp')
        
    run_args = dict({'itermaxin' : 5, 
                     'runmax'    : 2, 
                     'infile'    : 'test.nex', 
                     'outfolder' : './temp'})
    f81(run_args)

if __name__ == "__main__":
    # If you want to use this from command line without
    # django's PYTHONPATH then change this to your local 
    # project's path.
    project_path = r'/Users/slinkola/STAM/Stemweb/'
    main()
else:
    import Stemweb.settings as settings
    project_path = settings.SITE_ROOT

  
