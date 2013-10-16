'''
Functions for executing local and external algorithm runs.
'''
import os

from django.shortcuts import get_object_or_404
from .models import InputFile, Algorithm, AlgorithmRun

from Stemweb.settings import MEDIA_ROOT
import utils

def local(form, algo_id, request):
	''' Make a local algorithm run for logged in user.
	
	Returns AlgorithmRun id.
	'''
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
	
	
	run_args = utils.build_local_args(form, algorithm_id = algo_id, request = request)
	current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
											algorithm = Algorithm.objects.get(id = algo_id), 
											user = request.user,
                                        	folder = os.path.join(MEDIA_ROOT, run_args['folder_url']))
	current_run.save()	# Save to ensure that id generation is not delayed.
	kwargs = {'run_args': run_args, 'algorithm_run': current_run.id}
	call = algorithm.get_callable(kwargs)
	call.delay(**kwargs)
	return current_run.id


def external(form, algo_id, request):
	''' Make external algorithm run for request that came from trusted ip.
	
	First creates the InputFile object of the request.POST's json data and saves
	it. Then executes the actual run.
	
	Returns AlgorithmRun id.
	'''
	
	
	
	algorithm = get_object_or_404(Algorithm, pk = algo_id)
	run_args = utils.build_external_args(form, algorithm_id = algo_id, request = request)
	current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
										algorithm = Algorithm.objects.get(id = algo_id), 
                                    	folder = run_args['outfolder'],
                                    	external = True)
	pass