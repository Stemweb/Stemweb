'''
Functions for executing local and external algorithm runs.
'''
import os

from django.shortcuts import get_object_or_404
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
	call.apply_async(kwargs = kwargs, link = external_algorithm_run_finished.s(rid), \
					link_error = external_algorithm_run_error.s(rid))
	return current_run.id


def external(json_data, algo_id, request):
	''' Make external algorithm run for request that came from trusted ip.
	
	First creates the InputFile object of the request.POST's json's data and saves
	it. Then executes the actual run.
	
	Returns AlgorithmRun id.
	'''
	from Stemweb.files.models import InputFile
	
	
	
	parameters = json_data['parameters']
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
	run_args = utils.build_external_args(parameters, \
			algorithm_name = algorithm.name, request = request)
	current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
										algorithm = Algorithm.objects.get(id = algo_id), 
                                    	folder = run_args['outfolder'],
                                    	external = True)
	pass


	