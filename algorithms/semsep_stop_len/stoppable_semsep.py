#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rpy2 import robjects
import time
import math
import saveres
import sys

if __name__ == '__main__':
	sys.path.append("/Users/slinkola/STAM/Stemweb/algorithms/")
	
from stoppable_algorithm import StoppableAlgorithm
from stoppable_algorithm import Observer
from stoppable_algorithm import synchronized

class Semsep_f81(StoppableAlgorithm):
	'''
		Concurrent implementation of Semsep where temporary results are writed
		into file at algorithms run time and all observers are notified of new 
		results.
		
		Check documentation of StoppableAlgorithm for details.
	'''
	
	def __algorithm__(self, run_args = None):
		# assign parameters
		infile = run_args['infile']
		runmax = run_args['runmax']
		itermaxin = run_args['itermaxin']
		approximation = 0 
		outfolder = run_args['outfolder']
		source = run_args['source']
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
				self._put_in_results(savevalue)	
				self._results_queue.close()
				break # if two runs are coverged, break and return
	
			if iteri < 10:
				itertime.append(sum(iterationrunres.rx2('itertime'))/len(iterationrunres.rx2('itertime')))
	
			if self._stop.value == 0:
				print (iteri)
				if iteri != int(math.ceil(itermaxin*0.1+3)):
					iterationrunres = iterationrun(runmax=runmax, approximation=approximation, runres = iterationrunres.rx2('runres'), bestres = iterationrunres.rx2('bestres'), iter = iteri, converge = iterationrunres.rx2('converge'))
					bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
					bestruntmp = bestruntmp1.rx2('bestruntmp')
					if bestqscore < bestruntmp1.rx2('bestqscore')[0]:#if qscore inceased output
						bestqscore = bestruntmp1.rx2('bestqscore')[0]
						bestlastruntmp = findbestlastrun(iterationrunres=iterationrunres, runmax=runmax)
						savevalue = {'iterationrunres':iterationrunres,'itertime':itertime, 'bestruntmp':bestruntmp,'bestlastruntmp':bestlastruntmp,'iteri':iteri,'outfolder':outfolder}
						self._put_in_results(savevalue)	
				else:# new start
					bestruntmp1 = findbestrun(iterationrunres=iterationrunres, runmax=runmax)
					bestruntmp = bestruntmp1.rx2('bestruntmp')
					iterationrunres = updateres(runmax=runmax, bestruntmp=bestruntmp, iterationrunres=iterationrunres)
			else:
				print ('stop in the middle')
				self._results_queue.close()
				break	
		
	#@synchronized(file_lock)		
	def _write_in_file_(self, result):
		'''
			Overrided method to call saveres.writefile
		'''
		self.file_lock.acquire()
		saveres.writefile(result)
		self.file_lock.release()
				
		
if __name__ == '__main__':

	run_args = dict({
					'itermaxin' :100, 
					'runmax'    : 2, 
					'infile'    : 'test.nex', 
					'outfolder' : './temp',
					'source':'/Users/slinkola/STAM/Stemweb/algorithms/semsep_stop_len/allunilen.r'})
	
	obs = Observer()
	obs2 = Observer()
	obs2.a = 2
	testrun = Semsep_f81(run_args = run_args)
	testrun.attach(obs)
	testrun.attach(obs2)
	testrun.start()
	time.sleep(3)
	testrun.stop()
	testrun.join()
	
	

	

