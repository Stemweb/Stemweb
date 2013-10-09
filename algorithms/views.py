'''
Created on Mar 28, 2012

@author: slinkola
'''
import time
import logging
import json

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required

#from Stemweb.third_party_apps.djangotasks import task_for_object, run_task

from .models import InputFile
from .models import Algorithm, AlgorithmRun, AlgorithmArg
from . import utils
import settings

def base(request):
	algorithms = Algorithm.objects.all()
	c = RequestContext(request, {"all_algorithms" : algorithms}) 
	return render_to_response("algorithms_base.html", c)

def details(request, algo_id, form = None):
	'''
		Details view of the given algorithm. Shows description and user's 
		previous runs with this algorithm. Also user is able to do a new run.
	'''
	algorithm = get_object_or_404(Algorithm, id = algo_id)
	context_dict = {'algorithm': algorithm}
	''' If we have been given a form don't build it. '''
	if form is None:
		form = algorithm.args_form(user = request.user, post = None)
	if form is not None and len(form.fields) > 0: context_dict['form'] = form
	previous_runs = None
	if request.user.is_authenticated():
		previous_runs = AlgorithmRun.objects.filter(user = request.user, algorithm = algo_id)
	context_dict['algorithm_runs'] = previous_runs
	context_dict['all_algorithms'] = Algorithm.objects.all()
	c = RequestContext(request, context_dict)
	return render_to_response("algorithms_details.html", c)
	
	
@login_required
def delete_runs(request):
	
	if request.method == 'POST':
		run_ids = request.POST.get('runs').split()
		runs = AlgorithmRun.objects.filter(id__in = run_ids)
			
		for r in runs:
			if r.user != request.user:
				logger = logging.getLogger('stemweb.algorithm_run')
				logger.error('AlgorithmRun %s:%s tried to be removed by wrong user id:%s' \
				% (r.algorithm.name, r.id, request.user.id))
				return HttpResponseBadRequest("You are trying to remove runs which are not owned by active user. \n The request could not be completed and has been logged.")
		
		for r in runs:
			#if r.finished == True:
			'''
				TODO: prompt that user has to stop the run before it can be 
				deleted.
			'''
			r.delete()
		
		return HttpResponse("Runs were deleted succesfully.")	
	return HttpResponseRedirect("/server_error")

	
@login_required
def run(request, algo_id):
	''' Run's the given algorithm with run_args spesified in request.POST if the
		form builded from them is valid.
	'''
	if request.method == 'POST':
		algorithm = get_object_or_404(Algorithm, pk = algo_id)
		form = algorithm.args_form(user = request.user, post = request.POST)
		if form.is_valid():
			run_args = utils.build_args(form, algorithm_id = algo_id, request = request)
			current_run = AlgorithmRun.objects.create(input_file = InputFile.objects.get(id = run_args['file_id']),
													algorithm = Algorithm.objects.get(id = algo_id), 
													user = request.user,
	                                            	folder = run_args['outfolder'])
			current_run.save()	
			kwargs = {'run_args': run_args, 'algorithm_run': current_run.id}
			call = algorithm.get_callable(kwargs)
			call.delay(**kwargs)
			return HttpResponseRedirect(reverse('algorithms_run_results_url', \
				kwargs = { 'run_id': current_run.id }))
	else:
		resp = render_to_response('404.html')
		resp.status_code = 404
		return resp
	
	return HttpResponseRedirect(reverse('algorithms_details_url', args = { algo_id }))

@login_required
def results(request, run_id):
	''' Results of the algorithm run by run_id. Runs user should be the same as 
		the one who send the request. '''
	run = get_object_or_404(AlgorithmRun, id = run_id)
	
	if request.user == run.user:
		c = RequestContext(request, {'algorithm_run': run})
		if run.finished:
			return render_to_response('algorithm_running_results.html', c)
		else:
			return render_to_response('algorithm_running_results.html', c)
		
	raise Http404


def available(request):
	''' Returns all available AlgorithmArg and Algorithm model instances in 
		json-format. '''
	return HttpResponse(serialize('json', list(AlgorithmArg.objects.all()) +\
			list(Algorithm.objects.all()), fields = ['pk', 'key', 'value', 'name', 'args']),\
			mimetype='application/json')
	
	
def process(request, algo_id):
	''' Process external servers algorithm run. '''
	ret = utils.validate_server(request)
	if not ret[0]:
		# IP not in trusted list
		error_message = json.dumps({'error': ret[1]})
		response = HttpResponse(error_message)
		response.status_code = 403
		return response
		
	if request.method == 'POST':
		json_data = json.loads(request.body)
		ret = utils.validate_json(json_data, algo_id)
		if not ret[0]:
			# No valid JSON
			error_message = json.dumps({'error': ret[1]})
			response = HttpResponse(error_message)
			response.status_code = 400
			return response
		else:
			# TODO: Do the actual processing.	
			return HttpResponse()
		
	else: 
		error_message = json.dumps({'error': 'Please use POST'})
		response = HttpResponse(error_message)
		response.status_code = 400
		return response
	
	



