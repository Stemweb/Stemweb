'''
Created on Mar 28, 2012

@author: slinkola
'''
import time
import logging

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

#from Stemweb.third_party_apps.djangotasks import task_for_object, run_task

from Stemweb.files.models import InputFile
from Stemweb.algorithms.models import Algorithm, AlgorithmRun
import utils
import settings
import threading 

def base(request):
	algorithms = Algorithm.objects.all()
	c = RequestContext(request, {"all_algorithms" : algorithms}) 
	return render_to_response("algorithms_base.html", c)

def details(request, algo_id, form = None):
	'''
		Details view of the given algorithm. Shows description and user's 
		previous runs with this algorithm. Also user is able to do a new run.
	'''
	algorithm = Algorithm.objects.get(id = algo_id)
	c_dict = {'algorithm': algorithm}
	''' If we have been given a form don't build it. '''
	if form is None: form = algorithm.build_form(user = request.user)
	''' Don't render form if it's none. '''
	if form is not None: c_dict['form'] = form
	algorithm_runs = None
	if request.user.is_authenticated():
		algorithm_runs = AlgorithmRun.objects.filter(user = request.user, algorithm = algo_id)
	c_dict['algorithm_runs'] = algorithm_runs
	c_dict['all_algorithms'] = Algorithm.objects.all()
	c = RequestContext(request, c_dict)
	return render_to_response("algorithms_details.html", c)

@login_required
def previous_runs(request, algo_id):
	algorithm_runs = AlgorithmRun.objects.filter(user = request.user, algorithm = algo_id)
	
	
@login_required
def delete_runs(request):
	if request.method == 'POST':
		run_ids = request.POST.get('runs').split()
		runs = AlgorithmRun.objects.filter(id__in = run_ids)
			
		for r in runs:
			if r.user != request.user:
				logger = logging.getLogger('stemweb.algorithm_run')
				logger.error('AlgorithmRun %s:%s tried to be removed by wrong user id:%s' % (r.algorithm.name), r.id, r.user.id)
				return HttpResponse("You are trying to remove runs which are not made by active user. \n The request could not be completed and has been logged.")
		
		for r in runs:
			#if r.finished == True:
			'''
					TODO: promp that user has to stop the run before it can be deleted.
			'''
			r.delete()
		
		return HttpResponse("Runs were deleted succesfully.")
		
	return HttpResponseRedirect("/server_error")

	
@login_required
def run(request, algo_id):
	'''
		Run's the given algorithm with run_args spesified in request.POST if the
		form builded from them is valid.
	'''
	if request.method == 'POST':
		algorithm = Algorithm.objects.get(pk = algo_id)
		form = algorithm.build_form(user = request.user, post = request.POST)
		if form.is_valid():
			run_args = utils.build_args(form, algorithm_id = algo_id, request = request)
			if run_args is None: return HttpResponseRedirect('/server_error')
			current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
													algorithm = Algorithm.objects.get(id = algo_id), 
													user = request.user,
	                                            	folder = run_args['outfolder'])
			current_run.save()	
			kwargs = {'run_args': run_args, 'algorithm_run': current_run.id}
			# get_callable returns callable method (__init__) and updates run_args
			# with "static" arguments (like separate files, which are machine
			# dependent).
			call = algorithm.get_callable(kwargs)
			instance = call(**kwargs)
			run = threading.Thread(target=instance.run())
			run.start()
			print run.isAlive()
			return HttpResponseRedirect('/algorithms/results/%s' % (current_run.id))
	else:
		form = None
		
	c = RequestContext(request, {'algo_id': algo_id, 'form': form})
	return render_to_response('algorithms_details.html', c)    

@login_required
def results(request, run_id):
	run = AlgorithmRun.objects.get(id = run_id)
	
	if request.user == run.user:
		c = RequestContext(request, {'algorithm_run': run})
		if run.finished:
			return render_to_response('algorithm_running_results.html', c)
		else:
			return render_to_response('algorithm_running_results.html', c)
		
	return HttpResponseRedirect('/server_errors')


