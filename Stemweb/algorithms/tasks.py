#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from queue import Queue, Empty
import multiprocessing as mp
import threading as th
import datetime
import os
import logging
from . import settings
import re
import json
import functools
import http.client
import urllib.request, urllib.error, urllib.parse

from .decorators import synchronized
from django.template.defaultfilters import slugify
from django.views.decorators.csrf import csrf_exempt

from celery import Task, shared_task
from Stemweb._celery import celery_app

from django.db import connection, connections

#from Stemweb.algorithms.settings import ALGORITHM_MEDIA_ROOT as algo_media_root ###   ImportError    ="=
import Stemweb.algorithms.settings 


class Observer():
	'''
		Small test class to demonstrate AlgorithmTask's observers
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

class AlgorithmTask(Task):
	'''
		Super class of all algorithms.
		
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
	
	# API - changeable elements
		
	# Human readable name of this algorithm. This name is used for celery's 
	# task registering and in future we will be syncing database models and 
	# callables together with this name. Override in subclass.
	name = None
	
	# Does this algorithm have resulting image. 
	has_image = False
	
	# Is image layout radial or not.
	radial_image = False
	
	# Does this algorithm have resulting newick tree.
	has_newick = False

	# Does this algorithm have a resulting networkx object
	has_networkx = False
	
	# Name of the key in result-dictionary that is intercepted and stored in 
	# self.algorithm_run.score at run time (database is updated with the new 
	# value). Intercepted value needs to be float or site might not render 
	# properly in browser.
	score_name = None

	# Name of the key in result-dictionary that is intercepted and stored in 
	# self.algorithm_run.current_iteration at run time (database is updated with 
	# the new value). Intercepted value needs to be float or site might not 
	# render properly in browser.
	iteration_name = None
	
	# Input file's key in run_args. This is the key to main input data that 
	# algorithm uses and should be same as the input file's key in 
	# AlgorithmArgs-table. 
	input_file_key = 'input_file'
	
	# API - accessable elements
	
	# Main running arguments given for this algorithm when instance was created.
	# This is a dictionary which has (atleast) keys for this algorithms 
	# arguments as described in AlgorithmArgs-table. This dictionary is passed 
	# in **kwargs to overrided __algorithm__ method.
	run_args = None
	
	# Images absolute path. This is automatically created when __init_run__ is
	# called if has_image is True. Use this path when you want to create 
	# resulting image for the algorithm run. 
	image_path = None 
	
	# Newicks absolute path. This is automatically created when __init_run__ is
	# called if has_newick is True. Use this path when you want to create 
	# resulting newick tree for the algorithm run. 
	newick_path = None
	
	# AlgorithmRun model INSTANCE this algorithm is referencing.
	algorithm_run = None
	
	### You don't probably need any of the following. ###
	
	# Always subclass this class for any algorithm tasks.
	abstract = True
	
	# Queue where new results are put before they are written to file.
	# This should be only accessed via algorithm instance itself.
	_results_queue = Queue()
	
	# Stop sign for algorithm. It's shared value because algorithm is ran in 
	# different thread. __algorihm__ should stop it's run in short future 
	# when this value changes to 1.
	_stop = mp.Value('b', 0)
	
	# Child process where __algorithm__ is run.
	_algorithm_thread = None		### used indeed!
	
	# Observers which are notified when new results are written to file. 
	_observers = []
	
	# Locks for different parts of class. Always acquire lock before any 
	# operations considering file reading/writing, manipulating _observers or
	# _results_queue
	
	# Lock for file reading and writing operations.
	file_lock = th.Lock()
	# Lock for manipulating _observers
	observer_lock = th.Lock()
	# Lock for _results_queue. 
	result_lock = th.Lock()

			
	def __init_run__(self, *args, **kwargs):
		''' Celery calls __init__ only once when it is started for every task.
			So we need to use this mock up init to initialize all the runs 
			separately. Method initializes algorithms thread locks and results
			queue and sets up image and newick path.
			
		'''
	
		self.run_args = kwargs.pop('run_args', None)			
		run_id = kwargs.pop('algorithm_run', None)

		if run_id is not None:
			from Stemweb.algorithms.models import AlgorithmRun
			self.algorithm_run = AlgorithmRun.objects.get(pk = run_id)
			slug_name = slugify(self.algorithm_run.algorithm.name)
			#for item in self.run_args.items():
				#print('######### key-value pair = ', item)
				#print ('############## arg.value= ',arg.value ,'==================' )
				#print ('############## arg.key= ',arg.key ,'==================' )

			#print ('###### self.input_file_key =', self.input_file_key, '++++++++++++++++++')
			file_name = os.path.splitext(os.path.basename(self.run_args[self.input_file_key]))[0]
			#print ('###### AlgorithmTask.__init_run__.file_name =', file_name, '++++++++++++++++++')
			self.input_file_name = file_name
			self.run_args['outfolder'] = self.algorithm_run.folder
			# e.g.: self.algorithm_run.folder:   /home/stemweb/Stemweb/media/results/runs/neighbour-net/15/YHDSCLFD
			if self.has_image:
				self.algorithm_run.image = os.path.join(self.run_args['folder_url'], \
					'%s_%s.png' % (file_name, slug_name))
				self.image_path = os.path.join(self.algorithm_run.folder, \
					'%s_%s.png' % (file_name, slug_name))
			if self.has_newick:
				self.algorithm_run.newick = os.path.join(self.run_args['folder_url'],\
				'%s_%s.tre' % (file_name, slug_name))
				self.newick_path = os.path.join(self.algorithm_run.folder,\
				'%s_%s.tre' % (file_name, slug_name))
			if self.has_networkx:
				self.algorithm_run.nwresult_path = os.path.join(self.run_args['folder_url'],\
				'%s_%s.json' % (file_name, slug_name))
				# e.g.: results/runs/neighbour-net/15/YHDSCLFD/20210118-170328-YXPGWOPK_neighbour-net.json
				self.nwresult_path = os.path.join(self.algorithm_run.folder,\
				'%s_%s.json' % (file_name, slug_name))
				# e.g.: /home/stemweb/Stemweb/media/results/runs/neighbour-net/15/YHDSCLFD/20210118-170328-YXPGWOPK_neighbour-net.json


			self.algorithm_run.save()
		
		if 'radial' in self.run_args:
			if self.run_args['radial'] == True:	# Make radial image
				self.radial_image = True
			
		obs = kwargs.pop('observers', None)
	
		self._stop = mp.Value('b', 0)
		self._results_queue = Queue()
		self._algorithm_thread = None
		self._observers = []
		self.file_lock = th.Lock()
		self.observer_lock = th.Lock()
		self.result_lock = th.Lock()
		
		if not obs is None:
			for o in obs:
				self.attach(o)
			
						
	def stop(self, request = None):
		'''
			Call this method to stop the child processes and cease algorithm's
			run gracefully. All subclasses must ensure that calling this
			function will make algorithm stop without exceptions and final
			results from algorithm are written to hard drive.
		'''
		if (self.algorithm_run is None):
				self.algorithm_run.process = None
				self._stop.value = 1
		
					
	@synchronized(observer_lock)	
	def attach(self, observer):
		'''
			Attach observer who is notified when algorithm has written new 
			data. Observer needs to have 'update' method which accepts
			atleast one argument.
		'''	
		assert hasattr(observer,'update')
		assert observer.update.__code__.co_argcount > 0
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
			
			Remember to set self._stop.value = 1 before method returns.
			
			run_args: 	Running arguments as dictionary,that are passed to the 
						subclassing algorithm run. run_args always have fixed 
						key "outfolder" that is the absolute path to the folder
						where algorithm should store all it's results. It should
						NOT be changed during the subclassing algorithm's run!
		'''
		pass

	
	def run(self, *args, **kwargs):
		'''
			Called when task is getting executed. Don't override unless you 
			have very good reason to do so. 
		'''
		self.__init_run__(*args, **kwargs)
		
		self.logger = logging.getLogger('stemweb.algorithm_run')
		self.logger.info('AlgorithmRun started: %s:%s output:%s ' % \
			(self.algorithm_run.algorithm.name, self.algorithm_run.id, \
			self.algorithm_run.folder))

		self._algorithm_thread = th.Thread(target = self.__algorithm__, 
										args = (self.run_args,), 
										name = 'stemweb_algorun')
		
		self._algorithm_thread.start()		## here class NJ(AlgorithmTask)  in  njc.py is called
		self.algorithm_run.status = settings.STATUS_CODES['running']
		print('I am running NOW as thread')
		#raise Exception("ERROR: this is an INTENDED test case exception from AlgorithmTask level ")   ### a manual test case 
		self.algorithm_run.save()			## here again class NJ(AlgorithmTask)  in  njc.py is called
		
		# TODO: Fix me st000pid busy wait.  #### INSERTED BY PREVIOUS DEVELOPER
		while self._stop.value == 0:
			if not self._algorithm_thread.isAlive(): break
			self._read_from_results_()	

		self._finalize_()		##  status can be being set either to 'finished' or to 'failure'
		if self.algorithm_run.status == settings.STATUS_CODES['failure']:			### failure status was set during inherited classtask (e.g.: njc algorithm run)
			request = exc = traceback = ''
			algorun_extras_dictionary = json.loads(self.algorithm_run.extras)   ###  algorun.extras is of type unicode-string
			return_host = algorun_extras_dictionary["return_host"]
			return_path = algorun_extras_dictionary["return_path"]
			### probably not needed here? ToDo!!! retest failure case (both scenarios: commented out or not)
			#print '########### calling ext_algo_run_error NOT as errback #######################'
			#external_algorithm_run_error(request, exc, traceback, self.algorithm_run.id, return_host, return_path)

		# Return newick as string for simplified callbacks of external runs.
		if self.has_newick: 
			nwk = ""
			if self.algorithm_run.status == settings.STATUS_CODES['finished']:
				with open(self.newick_path, 'r') as f:
					nwk = f.read()
			return nwk

		# Return network graph (as json object?) for simplified callbacks of external runs.
		if self.has_networkx:
			ntwrk = ""
			if self.algorithm_run.status == settings.STATUS_CODES['finished']:
				with open(self.nwresult_path, 'r') as f:
					ntwrk = f.read()
			return ntwrk

	
		
	def _finalize_(self):
		# Just be sure that all the results have been written to queue.
		time.sleep(0.3)
		self._read_from_results_()
		self._algorithm_thread.join()
		
		if self.algorithm_run is not None:
			''' 
				Need to get the right object again if there has been some 
				modifications by other tasks when algorithm was running.
			'''
			from Stemweb.algorithms.models import AlgorithmRun
			self.algorithm_run = AlgorithmRun.objects.get(pk=self.algorithm_run.id)
			if self.algorithm_run.status != settings.STATUS_CODES['failure']: ## failure was set during njc algorithm run; we want to keep this
				self.algorithm_run.status = settings.STATUS_CODES['finished']
			self.algorithm_run.end_time = datetime.datetime.now()
			self.algorithm_run.pid = -1
			self.algorithm_run.save()
		else:
			self.logger.info('Unknown %s AlgorithmRun ended' % (type(self)))

		self.logger.info('AlgorithmRun ended: %s:%s' % \
			(self.algorithm_run.algorithm.name, self.algorithm_run.id))
	
		
	@synchronized(result_lock)
	def _put_in_results_(self, value):
		''' Delete old objects from _results_queue and put new in. '''
		while True:
			try:
				cur = self._results_queue.get(timeout = 0.01)
				del cur
			except:
				break
		self._results_queue.put(value, block = True)
	
	
	@synchronized(result_lock)	
	def __get_from_results__(self):
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
				result = self.__get_from_results__()	
				if self.score_name in list(result.keys()) and self.algorithm_run is not None:
					self.algorithm_run.score = result[self.score_name]
					self.algorithm_run.save()
					self.logger.info("AlgorithmRun %s:%s got better score %s" % \
						(self.algorithm_run.algorithm.name, self.algorithm_run.id, \
						result[self.score_name]))
				if self.iteration_name in list(result.keys()) and self.algorithm_run is not None:
					self.algorithm_run.current_iteration = result[self.iteration_name]
					self.algorithm_run.save()
					self.logger.info("AlgorithmRun %s:%s advanced to %s iteration" % \
						(self.algorithm_run.algorithm.name, self.algorithm_run.id, \
						result[self.iteration_name]))	
						
				self._write_in_file_(result)
				self._notify_()
			except Empty:
				pass	
			except:
				self.logger('AlgorithmRun %s:%s writing to file failed in %s' % \
					(self.algorithm_run.algorithm.name, self.algorithm_run.id, \
					self.run_args['outfolder']))
			
			time.sleep(0.1)

			
	def _write_in_file_(self, result):
		''' Override in subclass. Write result objects to given output paths 
			usually self.image_path and self.newick_path. Also the 
			self.algorithm_run.folder is available, but subdirs to that folder
			need to be created by the subclassing algorithm. 
		
			If the subclass writes only the final results then it doesn't have 
			to use this and it can instead write the results in the overrided
			__algorithm__ method.
		'''
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


@shared_task	
def external_algorithm_run_error(*args, run_id=None, return_host=None, return_path=None):	
	''' Callback task in case external requested algorithm run fails.  
		note these in *args packed arguments, handed over but NOT visible in the call execute_algorithm.py/external/call.apply_async(link_error = ....)
		- args[0]:  various celery task request infos, e.g.:
			stemweb_py37_1  | [2021-07-21 18:57:20,935: WARNING/MainProcess] <Context: {'lang': 'py', 'task': 'RHM', 'id': '9ab8f80e-d59e-4c9c-a171-72f112b37be6', 'shadow': None, 'eta': None, 'expires': None, 'group': None, 'group_index': None, 'retries': 0, 'timelimit': [None, None], 'root_id': '9ab8f80e-d59e-4c9c-a171-72f112b37be6', 'parent_id': None, 'argsrepr': '()', 'kwargsrepr': "{'run_args': {'imax': 1000000, 'infolder': '/home/stemweb/Stemweb/media/files/csv/20210721-185720-IPTMRYJA.csv', 'folder_url': 'results/runs/rhm/5/ZZLF7CT5'}, 'algorithm_run': 1}", 'origin': 'gen68@4eb7f48633ed', 'reply_to': 'b605934d-b5ea-3a17-b482-f80ff1486dec', 'correlation_id': '9ab8f80e-d59e-4c9c-a171-72f112b37be6', 'hostname': 'celery@4eb7f48633ed', 'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': None}, 'args': [], 'kwargs': {'run_args': {'imax': 1000000, 'infolder': '/home/stemweb/Stemweb/media/files/csv/20210721-185720-IPTMRYJA.csv', 'folder_url': 'results/runs/rhm/5/ZZLF7CT5'}, 'algorithm_run': 1}, 'callbacks': [{'task': 'Stemweb.algorithms.tasks.external_algorithm_run_finished', 'args': [], 'kwargs': {'run_id': 1, 'return_host': 'stemmaweb.net:443', 'return_path': '/stemmaweb/stemweb/result'}, 'options': {}, 'subtask_type': None, 'immutable': False, 'chord_size': None}], 'errbacks': [{'task': 'Stemweb.algorithms.tasks.external_algorithm_run_error', 'args': [], 'kwargs': {'run_id': 1, 'return_host': 'stemmaweb.net:443', 'return_path': '/stemmaweb/stemweb/result'}, 'options': {}, 'subtask_type': None, 'immutable': False, 'chord_size': None}], 'chain': None, 'chord': None, '_children': []}>
		- args[1]:  exception / error text, e.g.:
			Worker exited prematurely: signal 11 (SIGSEGV) Job: 0.
			or e.g.:
			[Errno 2] No such file or directory: '/home/stemweb/Stemweb/media/results/runs/rhm/5/7OCRD3Y4/20210804-181608-BSBLR3EH_rhm.tre'
		- args[2]: empty or Traceback, e.g:
			stemweb_py37_1  | [2021-08-04 18:16:09,243: WARNING/ForkPoolWorker-3] Traceback (most recent call last):
			stemweb_py37_1  |   File "/usr/local/lib/python3.7/site-packages/celery/app/trace.py", line 412, in trace_task
			stemweb_py37_1  |     R = retval = fun(*args, **kwargs)
			stemweb_py37_1  |   File "/usr/local/lib/python3.7/site-packages/celery/app/trace.py", line 704, in __protected_call__
			stemweb_py37_1  |     return self.run(*args, **kwargs)
			stemweb_py37_1  |   File "/home/stemweb/Stemweb/algorithms/tasks.py", line 318, in run
			stemweb_py37_1  |     with open(self.newick_path, 'r') as f:
			stemweb_py37_1  | FileNotFoundError: [Errno 2] No such file or directory: '/home/stemweb/Stemweb/media/results/runs/rhm/5/7OCRD3Y4/20210804-181608-BSBLR3EH_rhm.tre'

			or None

	'''
	print ('######################## external algorithm run failed :-(( ################################')
	print ('args[0]=', args[0], '+++++++++++++++++' )
	print ('args[1]=', args[1], '+++++++++++++++++' )
	#print ('args[2]=', args[2], '+++++++++++++++++' )
	from Stemweb.algorithms.models import AlgorithmRun

	try:
		algorun = AlgorithmRun.objects.get(pk = run_id)			### django-DB connection can be lost after errors in RHM c-extension 
	except OperationalError:
		print ('\n ############ close and restore damaged DB connections #############\n')
		for conn in connections.all():
			conn.close_if_unusable_or_obsolete()			### close damaged DB connections

		#cursor = connection.cursor()	### Will result in: jango.db.utils.InterfaceError: connection already closed
		
		connection.cursor().execute('SELECT 1;')			### restore DB connections

		### get object again from DB:
		algorun = AlgorithmRun.objects.get(pk = run_id)

	if algorun.status == settings.STATUS_CODES['running']:
		error_message = args[1]
		#print (error_message)
		algorun.status = settings.STATUS_CODES['failure']
		algorun.error_msg = error_message   ### for later usage in algorithms/views.py/jobstatus()
	else:									### else: status 'failure' was already set during njc-run
		error_message = algorun.error_msg

	algorun.end_time = datetime.datetime.now()
	algorun.save()
	
	ret = {
		'jobid': run_id,
		'statuscode': algorun.status,
		#'algorithm': algorun.algorithm.name,
		#'start_time': str(algorun.start_time),
		##'end_time': str(algorun.end_time),
		'result': error_message
		}
	
	try: 
		extra_json = json.loads(algorun.extras)
		ret.update(extra_json)
	except: 
		pass

	
	class BoundHTTPHandler(urllib.request.HTTPHandler):

		def __init__(self, source_address=None, debuglevel=0):
			urllib.request.HTTPHandler.__init__(self, debuglevel)
			self.http_class = functools.partial(http.client.HTTPConnection, source_address=source_address)
	
		def http_open(self, req):
			return self.do_open(self.http_class, req)


	class BoundHTTPSHandler(urllib.request.HTTPSHandler):

		def __init__(self, source_address=None, debuglevel=0):
			urllib.request.HTTPSHandler.__init__(self, debuglevel)
			self.http_class = functools.partial(http.client.HTTPSConnection, source_address=source_address)
	
		def http_open(self, req):
			return self.do_open(self.http_class, req)


	source_port = 51000
	handler = BoundHTTPHandler(source_address=("0.0.0.0", source_port), debuglevel = 0)
	shandler = BoundHTTPSHandler(source_address=("0.0.0.0", source_port), debuglevel = 0)
	fixed_sourceport_opener = urllib.request.build_opener(shandler, handler)

	message = json.dumps(ret)
	data = message.encode('utf8')
	headers = {'Content-type': 'application/json; charset=utf-8'}
	targeturl = 'https://' + return_host + return_path	
	#targeturl = 'http://' + return_host + return_path
	req = urllib.request.Request(targeturl, data, headers)

	try: 
		#response = urllib.request.urlopen(req)	# standard request; not using dedicated source_port; alternative to next line
		response = fixed_sourceport_opener.open(req)	
		#content = response.read()
		#print (content)
	except urllib.error.HTTPError as e:
		#print (e.code)
		#print (e.reason)
		pass

@shared_task
def external_algorithm_run_finished(*args, run_id=None, return_host=None, return_path=None):
	''' Callback task in case external algorithm run finishes succesfully. '''
	#print('########### algo_run_finished called #######################')

	targeturl = None
	#return_path = 'stemmaweb/stemweb/result/'
	hostparts = return_host.split(':')
	match = re.search("^http(s)?:", return_host)		# check if return_host also contains the protocol http or https
	if match:
			host = (hostparts[1]).replace('/','')		# remove  //
			port = hostparts[2]
			targeturl = return_host + return_path
	else:
		host = hostparts[0]
		port = hostparts[1]

	#logger = logging.getLogger('stemweb.algorithm_run')
		
	from Stemweb.algorithms.models import AlgorithmRun
	algorun = AlgorithmRun.objects.get(pk = run_id)

	res = ""
	usedformat = ""
	if algorun.status == settings.STATUS_CODES['failure']: # if failure status was set in njc.py or during rhm calc, then keep it  (not detectable during tasks execution level)
		res = algorun.error_msg
		if slugify(algorun.algorithm.name) == 'neighbour-net':
			usedformat = 'networkx-graph as json'
		else:
			usedformat = 'newick'
	else:	
		algorun.status = settings.STATUS_CODES['finished']
		if slugify(algorun.algorithm.name) == 'neighbour-net':
		#if algorun.algorithm.name == 'Neighbour Net' or algorun.algorithm.name == 'neighbour-net':
			with open(os.path.join(Stemweb.algorithms.settings.ALGORITHM_MEDIA_ROOT, AlgorithmRun.objects.get_or_none(pk = run_id).nwresult_path), 'r') as f:
				res = f.read()						### read networkx-graph-string from file (stored as json)
			usedformat = 'networkx-graph as json'
		else:
			with open(os.path.join(Stemweb.algorithms.settings.ALGORITHM_MEDIA_ROOT, AlgorithmRun.objects.get_or_none(pk = run_id).newick), 'r') as f:
				res = f.read()						### read newick-string from file
			usedformat = 'newick'
	algorun.save()
	algorun_extras_dictionary = json.loads(algorun.extras)   ###  algorun.extras is of type unicode-string
	text_id = algorun_extras_dictionary["textid"]
	ret = {
			'jobid': run_id,
			'status': algorun.status,			###  status-code
			'algorithm': algorun.algorithm.name,
			'textid': text_id,
			'start_time': str(algorun.start_time),
			'end_time': str(algorun.end_time),
			#'newick_path': algorun.newick,
			#'result': newick_result,          ### unfortunately newick_result is not handed over by parent of this callback function
			'result': res,					   
			'format': usedformat
			}	
	
	"""
	according to a proposal at:
	https://stackoverflow.com/questions/1150332/source-interface-with-python-and-urllib2
	This gives us a custom urllib2.HTTPHandler implementation that is source_address aware. We can add it to a new urllib2.OpenerDirector
	
	the same works for urllib.request used in python3 (instead of urllib2 used in python2.7) 
	"""

	class BoundHTTPHandler(urllib.request.HTTPHandler):

		def __init__(self, source_address=None, debuglevel=0):
			urllib.request.HTTPHandler.__init__(self, debuglevel)
			self.http_class = functools.partial(http.client.HTTPConnection, source_address=source_address)
	
		def http_open(self, req):
			return self.do_open(self.http_class, req)


	class BoundHTTPSHandler(urllib.request.HTTPSHandler):

		def __init__(self, source_address=None, debuglevel=0):
			urllib.request.HTTPSHandler.__init__(self, debuglevel)
			self.http_class = functools.partial(http.client.HTTPSConnection, source_address=source_address)
	
		def http_open(self, req):
			return self.do_open(self.http_class, req)


	source_port = 51000
	handler = BoundHTTPHandler(source_address=("0.0.0.0", source_port), debuglevel = 0)
	shandler = BoundHTTPSHandler(source_address=("0.0.0.0", source_port), debuglevel = 0)
	fixed_sourceport_opener = urllib.request.build_opener(shandler, handler)

	message = json.dumps(ret)
	data = message.encode('utf8')
	headers = {'Content-type': 'application/json; charset=utf-8'}
	#url = 'https://stemmaweb.net:443/stemmaweb/stemweb/result/'
	#req = urllib.request.Request(url, data, headers)

	if targeturl != None:
		req = urllib.request.Request(targeturl, data, headers)
	else:
		targeturl = 'https://' + return_host + return_path
		try:
			req = urllib.request.Request(targeturl, data, headers)
		except:
			targeturl = 'http://' + return_host + return_path
			req = urllib.request.Request(targeturl, data, headers)


	#print req.get_full_url()		### e.g.: https://stemmaweb.net:443/stemmaweb/stemweb/result/
	#print req.get_method()          ### POST
	#print req.(get_data) 
            
	try: 
		#response = urllib.request.urlopen(req)	### standard request, using any free source port
		response = fixed_sourceport_opener.open(req)	
		# content = response.read()
		# print (content)
	except urllib.error.HTTPError as e:
		# print (e.code)
		# print (e.reason)
		pass


class ClassBasedAddingTask(Task):
	def __init__(self, *args, **kwargs):
		pass

	def run(self, *args, **kwargs):
		result = args[0] + args[1]
		print('############ AddingTasks result: ###############', result, '+++++++++++++++++++++++++++++++')
		return	result

ClassBasedAddingTask = celery_app.register_task(ClassBasedAddingTask())


@shared_task
def adding_task(x, y, items=[]):
    result = x + y
    if items:
        for x, y in items:
            result += (x + y)
    return result

import adding ### adding is a c-extension (see addingmodule.c and setup_c_addingmodule.py)
@shared_task
def adding_c_task(x, y):
	result = adding.add(x,y)
	return result

### adding_c_task(3,2)
