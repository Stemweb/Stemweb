'''
Created on Mar 28, 2012

@author: slinkola
'''
import time
import logging
import json
import os

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest

from django.http import HttpRequest

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import csrf_exempt

from bs4 import BeautifulSoup as bs

from .models import Algorithm, AlgorithmRun, AlgorithmArg
from . import utils
from . import execute_algorithm
from .settings import STATUS_CODES
from .settings import ALGORITHM_MEDIA_ROOT as algo_media

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
	''' Delete runs that are present in request.POST in 'runs' paramater.
	
	If any of the run id's don't belong to the user making the request, does not 
	delete any of the runs.
	'''
	
	if request.method == 'POST':
		run_ids = request.POST.get('runs').split()
		runs = AlgorithmRun.objects.filter(id__in = run_ids)
			
		for r in runs:
			if r.user != request.user:
				logger = logging.getLogger('stemweb.algorithm_run')
				logger.error('AlgorithmRun %s:%s tried to be removed by wrong user id:%s' \
				% (r.algorithm.name, r.id, request.user.id))
				return HttpResponseBadRequest("You are trying to remove runs which are not owned by active user.\nThe request could not be completed and has been logged.")
		
		for r in runs:
			#if r.finished == True:
			# TODO: prompt that user has to stop the run before it can be 
			# deleted. 
			r.delete()
		
		return HttpResponse("Runs were deleted succesfully.")	
	return HttpResponseRedirect("/server_error")

	
@login_required
def run(request, algo_id):
	''' Run's the given algorithm with arguments spesified in request.POST if 
		the form builded from them is valid for the given algorithm.
	'''
	if request.method == 'POST':
		algorithm = get_object_or_404(Algorithm, pk = algo_id)
		form = algorithm.args_form(user = request.user, post = request.POST)
		if form.is_valid():
			run_id = execute_algorithm.local(form, algo_id, request)
			return HttpResponseRedirect(reverse('algorithms_run_results_url', \
				kwargs = { 'run_id': run_id }))
	else:
		resp = render_to_response('404.html')
		resp.status_code = 404
		return resp
	
	return HttpResponseRedirect(reverse('algorithms_details_url', \
									kwargs = { 'algo_id' : algo_id }))

@login_required
def results(request, run_id):
	''' Results of the algorithm run by run_id. Runs user should be the same as 
		the one who send the request. '''
	run = get_object_or_404(AlgorithmRun, id = run_id)
	
	if request.user == run.user:
		c = RequestContext(request, {'algorithm_run': run})
		if run.status == STATUS_CODES['finished']:
			return render_to_response('algorithm_running_results.html', c)
		# TODO: different view for non-finished algorithms
		else:
			return render_to_response('algorithm_running_results.html', c)
		
	raise Http404


def available(request):
	''' Returns all available AlgorithmArg and Algorithm model instances in 
		json-format. '''
	return HttpResponse(serialize('json', list(AlgorithmArg.objects.all()) +\
			list(Algorithm.objects.all()), fields = ['pk', 'key', 'value', 'name', 'args', 'external']),\
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
		json_data = json.loads(request.body, encoding = 'utf8')
		ret = utils.validate_json(json_data, algo_id)
		if not ret[0]:
			# No valid JSON
			error_message = json.dumps({'error': ret[1]})
			response = HttpResponse(error_message)
			response.status_code = 400
			return response
		else:
			# JSON ok, will process the algorithm
			run_id = execute_algorithm.external(json_data, algo_id, request)
			message = json.dumps({
								'jobid': run_id,
								'status': AlgorithmRun.objects.get_or_none(pk = run_id).status})	
			response = HttpResponse(message)
			response.status_code = 200		
			return response
		
	else: 
		error_message = json.dumps({'error': 'Please use POST'})
		response = HttpResponse(error_message)
		response.status_code = 400
		return response
	
	
def jobstatus(request, run_id):	
	ret = utils.validate_server(request)
	if not ret[0]:
		# IP not in trusted list
		error_message = json.dumps({'error': ret[1]})
		response = HttpResponse(error_message)
		response.status_code = 403
		return response
	else: 
		algo_run = AlgorithmRun.objects.get_or_none(pk = run_id)
		if algo_run is None: #or not algo_run.external: 
			error_message = json.dumps({'error': "No external algorithm run with given id"})
			response = HttpResponse(error_message)
			response.status_code = 400
			return response
		else:
			msg = {'job_id': run_id, 'status': algo_run.status}	
			if algo_run.status == STATUS_CODES['finished']:
				if algo_run.newick == '':
					msg['error'] = "Could not retrieve newick."
					return HttpResponse(json.dumps(msg))
				else:	
					nwk = ""
					with open(os.path.join(algo_media, algo_run.newick), 'r') as f:
						nwk = f.read()
					msg['result'] = nwk
					msg['format'] = 'newick'
					msg['algorithm'] = algo_run.algorithm.name
					msg['start_time'] = str(algo_run.start_time)
					msg['end_time'] = str(algo_run.end_time)
					return HttpResponse(json.dumps(msg, encoding = "utf8"))
			else: 
				return HttpResponse(json.dumps(msg))
	
	
def processtest(request):
	csv_file = "/Users/slinkola/STAM/data_sets/notre2.csv"
	csv = u""
	import codecs
	with codecs.open(csv_file, 'r', encoding = 'utf8') as f:
		csv = f.read()

	json_data = {
		'return_host': '127.0.0.1:8000',
		'return_path': '/algorithms/testresponse/',
		'userid': 42,
		'parameters': {
			'imax': 1		
			},
		'data': csv
		}
	msg = json.dumps(json_data, encoding = 'utf8')
	request = HttpRequest()
	request.method = 'POST'
	request.body = msg
	request.user = AnonymousUser
	request.META = {}
	request.META['REMOTE_ADDR'] = '127.0.0.1'
	request.META['SERVER_PORT'] = 8000
	return process(request, 2)


@csrf_exempt
def testresponse(request):
	if request.method == "POST":
		print json.loads(request.POST['json'], encoding = "utf8")
		
		return HttpResponse("OK")
	
	return HttpResponse("No POST")

	
