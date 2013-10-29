'''
Functions for executing local and external algorithm runs.
'''
import os
from datetime import datetime
import tempfile
import codecs

from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile

#from bs4 import BeautifulSoup as bs

from tasks import external_algorithm_run_error
from tasks import external_algorithm_run_finished

from settings import ALGORITHM_MEDIA_ROOT as algo_root
from .models import InputFile, Algorithm, AlgorithmRun
import utils


def local(form, algo_id, request):
	''' Make a local algorithm run for logged in user.
	
	Returns AlgorithmRun id.
	'''
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
	
	run_args = utils.build_local_args(form, algorithm_name = algorithm.name, request = request)
	current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
											algorithm = Algorithm.objects.get(id = algo_id), 
											user = request.user,
                                        	folder = os.path.join(algo_root, run_args['folder_url']))
	current_run.save()	# Save to ensure that id generation is not delayed.
	rid = current_run.id
	kwargs = {'run_args': run_args, 'algorithm_run': rid}
	call = algorithm.get_callable(kwargs)
	call.apply_async(kwargs = kwargs)
	return current_run.id


def external(json_data, algo_id, request):
	''' Make external algorithm run for request that came from trusted ip.
	
	First creates the InputFile object of the request.POST's json's data and saves
	it. Then executes the actual run.
	
	Returns AlgorithmRun id.
	'''
	from Stemweb.files.models import InputFile
	csv_file = tempfile.NamedTemporaryFile(mode = 'w', delete = False)
	# First write the file in the temporary file and close it.
	with codecs.open(csv_file.name, mode = 'w', encoding = 'utf8') as f:
		f.write(json_data['data'].encode('ascii', 'replace'))	

	# Then construct a mock up InMemoryUploadedFile from it for the InputFile
	mock_file = None
	input_file_id = None
	with open(csv_file.name, "r") as f:
		name =  datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + utils.id_generator() + ".csv"
		mock_file = InMemoryUploadedFile(file = f, field_name = 'file', name = name, \
									content_type = 'utf8', size = os.path.getsize(csv_file.name), charset = 'utf-8')	
			
		input_file = InputFile(name = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + utils.id_generator() + ".csv", 
                                  file = mock_file)  
		input_file.extension = 'csv'
		input_file.save() # Save to be sure input_file.id is created 
		input_file_id = input_file.id
	
	input_file = InputFile.objects.get(pk = input_file_id)
	parameters = json_data['parameters']
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
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
	current_run.save()	# Save to ensure that id generation is not delayed.
	rid = current_run.id
	user_id = json_data['userid']
	return_host = json_data['return_host']
	return_path = json_data['return_path']
	kwargs = {'run_args': run_args, 'algorithm_run': rid}
	call = algorithm.get_callable(kwargs)
	call.apply_async(kwargs = kwargs, link = external_algorithm_run_finished.s(rid, user_id, return_host, return_path), \
					link_error = external_algorithm_run_error.s(rid, user_id, return_host, return_path))
	return current_run.id

	