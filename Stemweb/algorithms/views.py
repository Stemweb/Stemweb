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
from django.views.decorators.csrf import csrf_exempt

#from bs4 import BeautifulSoup as bs

from .models import Algorithm, AlgorithmRun, AlgorithmArg
from . import utils
from . import execute_algorithm
from .settings import STATUS_CODES
from .settings import ALGORITHM_MEDIA_ROOT as algo_media

def base(request):
	algorithms = Algorithm.objects.all()
	c = RequestContext(request, {"all_algorithms" : algorithms}) 
	#return render_to_response("algorithms_base.html", c)
	return render_to_response("algorithms_base.html", c.flatten()) # avoids Type error "context must be a dict rather than RequestContext" (necessary since django-1.11)
        #return render_to_response("algorithms_base.html", {"all_algorithms" : algorithms})

def details(request, algo_id, form = None):
	'''
		Details view of the given algorithm. Shows description and 
		previous runs with this algorithm. Also it is possible to do a new run.
	'''
	algorithm = get_object_or_404(Algorithm, id = algo_id)
	context_dict = {'algorithm': algorithm}
	''' If we have been given a form don't build it. '''
	if form is None:
		form = algorithm.args_form(post = None)
	if form is not None and len(form.fields) > 0: context_dict['form'] = form
	previous_runs = None
	previous_runs = AlgorithmRun.objects.filter(algorithm = algo_id)
	context_dict['algorithm_runs'] = previous_runs
	context_dict['all_algorithms'] = Algorithm.objects.all()
	#c = RequestContext(request, context_dict)
	#return render_to_response("algorithms_details.html", c)
        return render_to_response("algorithms_details.html", context_dict)	# avoids Type error "context must be a dict rather than RequestContext" (necessary since django-1.11)

def delete_runs(request):
	''' Delete runs that are present in request.POST in 'runs' paramater.
	'''
	
	if request.method == 'POST':
		run_ids = request.POST.get('runs').split()
		runs = AlgorithmRun.objects.filter(id__in = run_ids)
			
		for r in runs:
			#if r.finished == True:
			# TODO: prompt that user has to stop the run before it can be 
			# deleted. 
			r.delete()
		
		return HttpResponse("Runs were deleted succesfully.")	
	return HttpResponseRedirect("/server_error")

	
def run(request, algo_id):
	''' Run's the given algorithm with arguments spesified in request.POST if 
		the form built from them is valid for the given algorithm.
	'''

	if request.method == 'POST':
		algorithm = get_object_or_404(Algorithm, pk = algo_id)
		form = algorithm.args_form(post = request.POST)
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

def results(request, run_id):
	''' Results of the algorithm run by run_id '''
 
	run = get_object_or_404(AlgorithmRun, id = run_id)
	
	#c = RequestContext(request, {'algorithm_run': run})
	if run.status == STATUS_CODES['finished']:
		#return render_to_response('algorithm_running_results.html', c)
                #return render_to_response('algorithm_running_results.html', c.flatten()) 
                return render_to_response('algorithm_running_results.html', {'algorithm_run': run})
	else:
		# TODO: different view for non-finished algorithms
		#return render_to_response('algorithm_running_results.html', c)
                return render_to_response('algorithm_running_results.html', {'algorithm_run': run})
                #pass 

	#raise Http404


@csrf_exempt
def available(request):
	''' Returns all available AlgorithmArg and Algorithm model instances in 
		json-format. '''
	return HttpResponse(serialize('json', list(AlgorithmArg.objects.all()) +\
			list(Algorithm.objects.all()), fields = ['pk', 'key', 'value', 'name', 'args', 'external', 'desc']),\
			content_type='application/json')
	

@csrf_exempt	
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
	
	
@csrf_exempt	
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
		if algo_run is None or not algo_run.external: 
			error_message = json.dumps({'error': "No external algorithm run with given id"})
			response = HttpResponse(error_message)
			response.status_code = 400
			return response

		# Construct basic response json
		msg = {
			'jobid': run_id, 
			'status': algo_run.status, 
			'algorithm': algo_run.algorithm.name,
			'start_time': str(algo_run.start_time)
			}
		# Load any extra information stored to algorithm run	
		try:
			extra_json = json.loads(algo_run.extras)
			msg.update(extra_json)
		except:
			pass
		
		# Construct algorithm run status depended key-value pairs.
		if algo_run.status == STATUS_CODES['finished']:
			if algo_run.newick == '':
				msg['error'] = "Could not retrieve newick."
				return HttpResponse(json.dumps(msg, encoding = "utf8"))
			else:	
				nwk = ""
				with open(os.path.join(algo_media, algo_run.newick), 'r') as f:
					nwk = f.read()
				msg['result'] = nwk
				msg['format'] = 'newick'
				msg['end_time'] = str(algo_run.end_time)
				return HttpResponse(json.dumps(msg, encoding = "utf8"))
		if algo_run.status == STATUS_CODES['failure']:
			msg['end_time'] = str(algo_run.end_time) 
		return HttpResponse(json.dumps(msg, encoding = "utf8"))

	
def processtest(request):
	#csv_file = "/Users/slinkola/STAM/data_sets/request4.json"
        csv_file ="/home/stemweb/Stemweb/media/datasets/parzival_aligned.csv"	
        csv = u""
	import codecs
	with codecs.open(csv_file, 'r', encoding = 'utf8') as f:
		csv = f.read()

	msg = csv
	request = HttpRequest()
	request.method = 'POST'
	request.POST = msg
	request.content_type = "application/json"
	request.META = {}
	request.META['REMOTE_ADDR'] = '127.0.0.1'
	request.META['SERVER_PORT'] = 8000
	execute_algorithm.external(json.loads(csv, encoding = 'utf8'), 1, request)
	return HttpResponse("ok")


@csrf_exempt
def testresponse(request):
	if request.method == "POST":
		print json.loads(request.body, encoding = "utf8")
		
		return HttpResponse("OK")
	return HttpResponse("No POST")

def testserver(request):
	ret = utils.validate_server(request)
	return HttpResponse(ret[0])
	

	
