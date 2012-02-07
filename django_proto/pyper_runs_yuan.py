#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from pyper import *		# Import PypeR -- Python based R-script interpreter 
from rpy2 import robjects
import saveres
import os
import time





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

    # Open log file to outfolder for possible debug.
    log_path = os.path.join(run_args['outfolder'], 'python_log.txt')
    run_log = open(log_path, 'w')
    run_log.writelines([time.ctime(), '\n'])
    run_log.close()

    # Probably could check that all running arguments are in there.
  
    R = robjects.r									# Make instance of R.
    source = r'%s/semsep/allf81.r' % (project_path)
    R.source(source)
    
    runf81 = R['runf81']
    run_log = open(log_path, 'a')
    run_log.writelines('***** f81res in R -format ***** \n')
    f81res = runf81(run_args['infile'],
                    run_args['runmax'],
                    run_args['itermaxin'])
    log_entry = '%s' % (f81res)
    run_log.writelines([log_entry, '\n'])    
    run_log.close()
    
    #get results to python
    run_log = open(log_path, 'a')    
    run_log.writelines('***** f81res in python format ***** \n')
    #f81resPython = robjects.default_ri2py(f81res)
    f81resPython = f81res
    print ('*********')
    print (type(f81resPython))
    log_entry = '%s' % (f81resPython)
    run_log.writelines([log_entry, '\n'])    
    run_log.close()
    
    # I tried both python and R format and they seem from log-file to be 
    # the same. 
    
    # This doesn't work atm.
    saveres.writefile(Rres=f81res, outfolder = run_args['outfolder'])

    return 1

# Small main program to test code
def main():
    os.mkdir('temp')
    run_args = dict({'itermaxin' : 5, 
                     'runmax'    : 2, 
                     'infile'    : 'test.nex', 
                     'outfolder' : './temp'})
    runsemf81(run_args)

if __name__ == "__main__":
    # If you want to use this from command line without
    # django's PYTHONPATH then change this to your local 
    # project's path.
    project_path = r'/home/fs/zou/Stemweb/'
    main()
else:
    from Stemweb import local
    project_path = local.lstrings.project_path

  
