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
def f81run(stopsign,runresque,run_args):
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
            savevalue = {'iterationrunres':iterationrunres,'itertime':itertime, 'bestruntmp':bestruntmp,'bestlastruntmp':bestlastruntmp,'iteri':(iteri-1),'outfolder':outfolder}
            runresque.put(savevalue,block=True)
            while stopsign.empty():
                time.sleep(0.1)
                try:
                    stopsign.put('stop now',timeout=0.1) # put results first, then stop sign
                except Empty:
                    print ('stop fails, do again')
            break # if two runs are coverged, break and return

        if iteri < 10:
            itertime.append(sum(iterationrunres.rx2('itertime'))/len(iterationrunres.rx2('itertime')))
            
        if stopsign.empty():
            print (iteri)
            if iteri != int(math.ceil(itermaxin*0.1+3)): 
                iterationrunres = iterationrun(runmax=runmax, approximation=approximation, runres = iterationrunres.rx2('runres'), bestres = iterationrunres.rx2('bestres'), iter = iteri, converge = iterationrunres.rx2('converge'))
                bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
                bestruntmp = bestruntmp1.rx2('bestruntmp')
                if bestqscore < bestruntmp1.rx2('bestqscore')[0]:#if qscore inceased output
                    bestqscore = bestruntmp1.rx2('bestqscore')[0]
                    bestlastruntmp = findbestlastrun(iterationrunres=iterationrunres, runmax=runmax)
                    savevalue = {'iterationrunres':iterationrunres,'itertime':itertime, 'bestruntmp':bestruntmp,'bestlastruntmp':bestlastruntmp,'iteri':iteri,'outfolder':outfolder}
                    runresque.put(savevalue,block=True)
            else:# new start
                bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
                bestruntmp = bestruntmp1.rx2('bestruntmp')

                iterationrunres = updateres(runmax=runmax, bestruntmp=bestruntmp, iterationrunres=iterationrunres)
        else:
            print ('stop in the middle')
            break

    
def f81(run_args):
    
    
    stopsign = multiprocessing.Queue()
    runresque = multiprocessing.Queue()
    f81runproc = multiprocessing.Process(target=f81run, args=(stopsign,runresque,run_args,))
    f81runproc.start()
    
    i = 0
    while stopsign.empty():
        time.sleep(0.1)
        i = i+1
        if i>5:
            while stopsign.empty():
                time.sleep(0.1)
                try:
                    stopsign.put('stop now',timeout=0.1) 
                except Empty:
                    print ('stop fails, do again')
        try:
            savevalue = runresque.get(timeout=0.1)
            saveres.writefile(iterationrunres=robjects.Vector(savevalue['iterationrunres']),itertime=savevalue['itertime'], bestruntmp=savevalue['bestruntmp'],bestlastruntmp=savevalue['bestlastruntmp'],iternow=savevalue['iteri'],outfolder=savevalue['outfolder'])
        except Empty:
            print ('no temperary results')
    while not runresque.empty():
        try:
            savevalue = runresque.get(timeout=0.1)
            saveres.writefile(iterationrunres=robjects.Vector(savevalue['iterationrunres']),itertime=savevalue['itertime'], bestruntmp=savevalue['bestruntmp'],bestlastruntmp=savevalue['bestlastruntmp'],iternow=savevalue['iteri'],outfolder=savevalue['outfolder'])
        except Empty:
            print ('all results have been printed')

    f81runproc.join()
    
    
run_args = dict({'itermaxin' :1000, 
'runmax'    : 2, 
'infile'    : 'test.nex', 
'outfolder' : './temp',
'source':'/home/zou/Desktop/Stemwebedit/semsep_stop/allf81.r'})


f81(run_args)
