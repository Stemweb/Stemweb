'''
Functions for executing local and external algorithm runs.
'''
import os
from datetime import datetime
from time import sleep
import tempfile
import codecs
import json
from cleanup import remove_old_results_db, remove_old_results_fs

from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile

#from bs4 import BeautifulSoup as bs

from tasks import external_algorithm_run_error
from tasks import external_algorithm_run_finished

from settings import ALGORITHM_MEDIA_ROOT as algo_root
from .models import InputFile, Algorithm, AlgorithmRun
import utils


def local(form, algo_id, request):
	''' Make a local algorithm run.
	    Returns AlgorithmRun id.
	'''
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
	
	run_args = utils.build_local_args(form, algorithm_name = algorithm.name, request = request)
	current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
						algorithm = Algorithm.objects.get(id = algo_id), 
                                        	folder = os.path.join(algo_root, run_args['folder_url']))
	current_run.save()	# Save to ensure that id generation is not delayed.
	rid = current_run.id
	kwargs = {'run_args': run_args, 'algorithm_run': rid}
	call = algorithm.get_callable(kwargs)
	call.apply_async(kwargs = kwargs)
	#call.apply(kwargs = kwargs)    # synchronous call for dev and test purpose
	return current_run.id


def external(json_data, algo_id, request):
	''' Make external algorithm run for request that came from trusted ip.
	
	First creates the InputFile object of the request.POST's json's data and saves
	it. Then executes the actual run.
	
	Returns AlgorithmRun id.
	
	TODO: Refactor me
	'''

	# remove outdated results in file system and in database compared with value in settings.KEEP_RESULTS_DAYS
	remove_old_results_fs()
	remove_old_results_db()


	from Stemweb.files.models import InputFile
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
	csv_file = tempfile.NamedTemporaryFile(mode = 'w', delete = False)
	ext = ""
	csv_data = None
	if algorithm.file_extension == 'csv': 
		csv_data = json_data.pop('data')
		ext = ".csv"
	elif algorithm.file_extension == 'nex': 
		from csvtonexus import csv2nex
		csv_data = csv2nex(json_data.pop('data'))	
		ext = ".nex"
		
	# First write the file in the temporary file and close it.
	with codecs.open(csv_file.name, mode = 'w', encoding = 'utf8') as f:
		f.write(csv_data.encode('ascii', 'replace'))	
		#json.dump(csv_data, f, indent = 4)

	# Then construct a mock up InMemoryUploadedFile from it for the InputFile
	mock_file = None
	input_file_id = None
	with open(csv_file.name, "r") as f:
		name =  datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + utils.id_generator() + ext
		mock_file = InMemoryUploadedFile(file = f, field_name = 'file', name = name, \
									content_type = 'utf8', size = os.path.getsize(csv_file.name), charset = 'utf-8')	
			
		input_file = InputFile(name = name, file = mock_file)  
		input_file.extension = ext
		input_file.save() # Save to be sure input_file.id is created 
		input_file_id = input_file.id
	
	input_file = InputFile.objects.get(pk = input_file_id)
	

	parameters = json_data['parameters']

	#print input_file
		
	input_file_key = ''
	for arg in algorithm.args.all():
		if arg.value == 'input_file':
			input_file_key = arg.key
		
	run_args = utils.build_external_args(parameters, input_file_key, input_file,
			algorithm_name = algorithm.name)
	current_run = AlgorithmRun.objects.create(input_file = input_file,
											algorithm = algorithm, 
											folder = os.path.join(algo_root, run_args['folder_url']),
											external = True)
		
	current_run.extras = json.dumps(json_data, encoding = 'utf8')
	current_run.save()	# Save to ensure that id generation is not delayed.
	rid = current_run.id
	return_host = json_data['return_host']
	return_path = json_data['return_path']
	kwargs = {'run_args': run_args, 'algorithm_run': rid}

	call = algorithm.get_callable(kwargs)

	# .s is a celery signature , used to concatenate tasks;  see:
	#  https://docs.celeryproject.org/en/master/userguide/calling.html
	#  https://docs.celeryproject.org/en/master/userguide/calling.html#linking-callbacks-errbacks
	call.apply_async(kwargs = kwargs, 					
					link = external_algorithm_run_finished.s(rid, return_host, return_path),
					link_error = external_algorithm_run_error.s(rid, return_host, return_path))


	#call.apply(kwargs = kwargs, link = external_algorithm_run_finished.s(rid, return_host, return_path))  ### synchronous task; for test purpose 

	sleep(0.3)	### needed for correct setting of task status ; seems to be a timing problem
	return current_run.id

	
