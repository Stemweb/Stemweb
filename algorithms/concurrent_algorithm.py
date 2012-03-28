#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Queue import Empty
import multiprocessing

def synchronized(lock):
	''' Synchronization decorator. '''

	def wrap(f):
		
		def syncedFunction(*args, **kw):
			lock.acquire()
			try: 
				return f(*args, **kw)
			finally: 
				lock.release()
		return syncedFunction
	
	return wrap


class Observer():
	'''
		Small test class to demonstrate ConcurrentAlgorithm's observers
		implementation. You don't need to subclass this for observers but 
		be sure to add update -method with similar behaviour.
	'''
	listening_to = None
	
	def __init__(self, listening = None):
		if hasattr(listening, 'attach'):
			self.listening_to = listening
			listening.attach(self)
		self.a = 1
			
	
	def update(self, new_data):
		self.listening_to.file_lock.acquire()
		'''
		Do your file reading here.	
		'''
		self.listening_to.file_lock.release()

		
class ConcurrentAlgorithm(multiprocessing.Process):
	'''
		Super class of all algorithms that are going to be stoppable from 
		webpage's user interface. 
		
		Call start() to run algorithm and stop() to.... stop. You can add 
		observers by attach(observer) method which are notified when algorithm
		writes new results to file. Observers must implement update() method
		which takes atleast one argument and they must acquire file_lock 
		from the instance of the subclass before they can read new results from 
		file. 
		
		When subclassing pay close attention that stop()-method works correctly
		and algorithm writes final results into file. You probably only need 
		to override methods __algorithm__ and _write_in_file_, but read 
		documentation carefully.
	'''
	
	# Running arguments given for this algorithm when instance was created.
	run_args = None
	# Queue where new results are put before they are written to file.
	# This should be only accessed via algorithm instance itself.
	_results_queue = multiprocessing.Queue()
	# Stop sign for algorithm. It's shared value because algorithm is ran in 
	# different thread. __algorihm__ should stop it's run in short future 
	# when this value changes to 1.
	_stop = multiprocessing.Value('b', 0)
	# Child process where __algorithm__ is run.
	_child_process = None
	# Observers which are notified when new results are written to file. 
	_observers = []
	
	# Locks for different parts of class. Always acquire lock before any 
	# operations considering file reading/writing, manipulating _observers or
	# _results_queue
	
	# Lock for file reading and writing operations..
	file_lock = multiprocessing.Lock()
	# Lock for manipulation _observers sequence
	observer_lock = multiprocessing.Lock()
	# Lock for _results_queue's manipulation. To be implemented.
	result_lock = multiprocessing.Lock()
			
	def __init__(self, run_args = None, observers = None):
		multiprocessing.Process.__init__(self)	
		self.run_args = run_args
		if not observers is None:
			for o in observers:
				self.attach(o)
			
						
	def stop(self):
		'''
			Call this method to stop the child processes and cease algorithm's
			run gracefully. All subclasses must ensure that calling this
			function will make algorithms stop without exceptions and final
			results from algorithm are written to disc.
		'''
		self._stop.value = 1
			
			
	@synchronized(observer_lock)	
	def attach(self, observer):
		'''
			Attach observer who is notified when algorithm has written new 
			data. Observer needs to have 'update' method which accepts
			atleast one argument.
		'''	
		assert hasattr(observer,'update')
		assert observer.update.func_code.co_argcount > 0
		if not observer in self._observers:	
			observer.listening_to = self
			self._observers.append(observer)
		
		
	@synchronized(observer_lock)		
	def deattach(self, observer):
		''' Remove observer from _observers if it was there. '''
		if observer in self._observers:
			self._observers.remove(observer)


	def __algorithm__(self, run_args = None):
		'''
			Main algorithm implementation for subclasses to override. 
			
			Method is invoked by run() method which is called when self.start()
			is called and self.run_args are passed to this method. Make sure 
			method stops it's run without exceptions when stop()-method is 
			called. 
			
			Algorithm should add any results that are going to be written in
			file to _results_queue. It's advised to acquire lock for this
			before actually using the queue.
		'''

				
	def run(self):
		'''
			Called with instance.start(). Don't override unless you have very 
			good reason to do so. 
		'''
		self._child_process = multiprocessing.Process(target=self.__algorithm__, args=(self.run_args,))
		self._child_process.start()	
		# TODO: Fix me st000pid busy wait.
		while self._stop.value == 0:
			self._read_from_results_()	
		# Read one last time if something was added after stop changed.
		time.sleep(0.3)
		self._read_from_results_()
		self._child_process.join()

		
	@synchronized(result_lock)
	def _put_in_results(self, value):
		''' Delete old objects from _results_queue and put new in. '''
		while True:
			try:
				cur = self._results_queue.get(timeout = 0.01)
				del cur
			except:
				break
		self._results_queue.put(value, block = True)
	
	
	@synchronized(result_lock)	
	def _get_from_results(self):
		return self._results_queue.get(block = True, timeout = 0.1)


	def _read_from_results_(self):
		'''
			Read new data from results_queue,write it to file and notify all
			observers about changes. File writing is done inside file_lock,
			which should be acquired by observers before any file reading is 
			done.	
		'''	
		while not self._results_queue.empty():
			try:
				result = self._get_from_results()		
				self._write_in_file_(result)
				self._notify_()
			except Empty:
				pass	
			except:
				print "Fatal error"
			time.sleep(0.01)

			
	def _write_in_file_(self, result):
		''' Override in subclass. Write result object to given output path. '''
		self.file_lock.acquire()
		# Do your file writing between the acquire and release.
		self.file_lock.release()
	
				
	@synchronized(observer_lock)	
	def _notify_(self):
		'''
			Notify observers that new data has been written. Observers should
			acquire instance's file_lock before reading data. 
		'''
		for o in self._observers:
			o.update(self)
		
		
if __name__ == '__main__':
	run_args = dict({
					'itermaxin' :100, 
					'runmax'    : 2, 
					'infile'    : 'test.nex', 
					'outfolder' : './temp',
					'source':'/Users/slinkola/STAM/Stemweb/algorithms/semsep_stop_len/allunilen.r'})
	
	
	
	testrun = ConcurrentAlgorithm(run_args)
	obs = Observer(testrun)
	testrun.attach(obs)
	
	testrun.start()
	time.sleep(1)
	testrun.stop()
	testrun.join()
	
	
