#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rpy2 import robjects
import os
import time
from rpy2 import *
import math
import saveres
import sys
from Queue import Empty
import multiprocessing
from multiprocessing import Process, Pipe


# run sem and put results in semresque
# stopsign no empty means stop now
def f81queue(stopsign,run_args):
    # assign parameters
    infile= run_args['infile']
    runmax=run_args['runmax']
    itermaxin=run_args['itermaxin']
    approximation=0 
    outfolder=run_args['outfolder']
    source=run_args['source']
    # load R functions
    R = robjects.r
    R.source(source) 
    initiationrun = R['initiationrun']
    iterationrun = R['iterationrun']
    findbestrun = R['findbestrun']
    updateres = R['updateres']
    findbestlastrun = R['findbestlastrun']

    
    # initiation
    initiationrunres = initiationrun(runmax=runmax, itermax=itermaxin, filein=infile, approximation=approximation)
    iterationrunres = initiationrunres
    itertime = []
    itertime.append(sum(iterationrunres.rx2('itertime'))/len(iterationrunres.rx2('itertime')))
    
    
    ## can only stop from here...
    bestqscore = -float('Inf')
    for iteri in range(2,itermaxin+1):
        if (sum(iterationrunres.rx2('converge'))==len(iterationrunres.rx2('converge'))):
            print ('converged')
            bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
            bestruntmp = bestruntmp1.rx2('bestruntmp')
            bestlastruntmp = findbestlastrun(iterationrunres=iterationrunres, runmax=runmax)
            saveres.writefile(iterationrunres=iterationrunres,itertime=itertime, bestruntmp=bestruntmp,bestlastruntmp=bestlastruntmp,iternow=iteri,outfolder=outfolder)
            break # if two runs are coverged, break and return

        if iteri < 10:
            itertime.append(sum(iterationrunres.rx2('itertime'))/len(iterationrunres.rx2('itertime')))
            
        if stopsign.empty():
            print (iteri)
            if iteri != int(math.ceil(itermaxin*0.1+3)): 
                iterationrunres = iterationrun(runmax=runmax, approximation=approximation, runres = iterationrunres.rx2('runres'), bestres = iterationrunres.rx2('bestres'), iter = iteri, converge = iterationrunres.rx2('converge'))
                bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
                bestruntmp = bestruntmp1.rx2('bestruntmp')
                if bestqscore < bestruntmp1.rx2('bestqscore')[0]: 
                ## if qscore increases, input current tree
                    bestqscore = bestruntmp1.rx2('bestqscore')[0]
                    saveres.writefilelite(iterationrunres=iterationrunres,itertime=itertime, bestruntmp=bestruntmp,iternow=iteri,outfolder=outfolder)
            else:# new start
                bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
                bestruntmp = bestruntmp1.rx2('bestruntmp')
                iterationrunres = updateres(runmax=runmax, bestruntmp=bestruntmp, iterationrunres=iterationrunres)
        else:
            print ('stop in the middle')
            bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
            bestruntmp = bestruntmp1.rx2('bestruntmp')
            bestlastruntmp = findbestlastrun(iterationrunres=iterationrunres, runmax=runmax)
            saveres.writefile(iterationrunres=iterationrunres,itertime=itertime, bestruntmp=bestruntmp,bestlastruntmp=bestlastruntmp,iternow=iteri,outfolder=outfolder)
            break

    #time.sleep(0.1)


def f81(run_args):
    run_argsqueue = run_args
    stopsign = multiprocessing.Queue()
    f81queueproc = multiprocessing.Process(target=f81queue, args=(stopsign,run_argsqueue,))
    f81queueproc.start()
    time.sleep(0.5)
    stopsign.put('stop now',block=True)
    f81queueproc.join()
    print ('------')
    
    
run_args = dict({'itermaxin' : 40, 
'runmax'    : 2, 
'infile'    : 'test.nex', 
'outfolder' : './temp',
'source':'/home/zou/Desktop/Stemwebedit/semsep/allf81.r'})


f81(run_args)

