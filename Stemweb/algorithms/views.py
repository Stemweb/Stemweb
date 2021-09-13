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
#from django.shortcuts import render_to_response
from django.shortcuts import render
from django.shortcuts import get_object_or_404
#from django.core.urlresolvers import reverse ### Django 2.0 removes the django.core.urlresolvers module, which was moved to django.urls in version 1.10.
from django.urls import reverse
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser

#from bs4 import BeautifulSoup as bs

from .models import Algorithm, AlgorithmRun, AlgorithmArg
from . import utils
from . import execute_algorithm
from .settings import STATUS_CODES
from .settings import ALGORITHM_MEDIA_ROOT as algo_media

def base(request):
	algorithms = Algorithm.objects.all()
	#context = RequestContext(request, {"all_algorithms" : algorithms}) 
    #return render_to_response("algorithms_base.html", {"all_algorithms" : algorithms})
	#return render(request, 'algorithms_base.html', context)  ### TypeError: context must be a dict rather than RequestContext.
	return render(request, 'algorithms_base.html', {"all_algorithms" : algorithms})

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
    #return render_to_response("algorithms_details.html", context_dict)	# avoids Type error "context must be a dict rather than RequestContext" (necessary since django-1.11)
	return render(request, 'algorithms_details.html', context_dict)

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
		#resp = render_to_response('404.html')
		resp = render(None,'404.html',None)
		resp.status_code = 404
		return resp
	
	return HttpResponseRedirect(reverse('algorithms_details_url', \
									kwargs = { 'algo_id' : algo_id }))

def results(request, run_id):
	''' Results of the algorithm run by run_id '''
 
	run = get_object_or_404(AlgorithmRun, id = run_id)
	#run.save()   ### why?
	#c = RequestContext(request, {'algorithm_run': run})
	if run.status == STATUS_CODES['finished']:
        #return render_to_response('algorithm_running_results.html', {'algorithm_run': run})
		return render(request, 'algorithm_running_results.html', {'algorithm_run': run})
	else:
		#return render_to_response('algorithm_running_results.html', c)
        #return render_to_response('algorithm_running_results.html', {'algorithm_run': run})
		return render(request, 'algorithm_running_results.html', {'algorithm_run': run})
	#else if run.status == STATUS_CODES['running']:
	# TODO: different view for non-finished algorithms ####  a MUST ToDo! ==> test with (simulated) long lasting calculations
	#	return render(request, 'algorithm_running_ongoing.html', {'algorithm_run': run})	         
	#	raise Http404


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
		try:
			json_data = JSONParser().parse(request)
		except Exception as e:			               # raising JSON parse error if JSON structure is invalid	
			response = HttpResponse(str(e))
			response.status_code = 400
			return response

		ret = utils.validate_json(json_data, algo_id)  # Validate that json contains all the needed parameters for external algorithm run.
		if not ret[0]:
			# No valid JSON
			error_message = json.dumps({'error': ret[1]})
			response = HttpResponse(error_message)
			response.status_code = 400
			return response
		else:
			# JSON ok, will process the algorithm
			run_id = execute_algorithm.external(json_data, algo_id, request)   # status will be set to "running" , except for RHM algorithm where it stays in "not_started"
			run = get_object_or_404(AlgorithmRun, id = run_id)

			if (run.status == STATUS_CODES['not_started']) and (algo_id == 2):	# algo_id 2: RHM algorithm
				# WORKAROUND: set status to "running" even if it is in state "not_started"
				# otherwise RHM algorithm-run would be set to "running " too late (i.e. after running/calculation is finished)
				run.status = statcode = STATUS_CODES['running']
				run.save()	    # save status also in object/DB; then it's visible in the django GUI as well
			else:
				statcode = run.status

			message = json.dumps({
								'jobid': run_id,
								'status': statcode
								})
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
		#if algo_run is None: 						###  temporarily removed external check to enable access via REST-API (JSON) for test purpose
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
			### algo_run.newick is the path + filename where the newick-string is stored, e.g.:
			### results/runs/neighbour-joining/15/B4Q6CTMO/20200929-115514-5GKHQ3UU_neighbour-joining.tre
			### full path is: /home/stemweb/Stemweb/media/results/runs/neighbour-joining/15/B4Q6CTMO/20200929-115514-5GKHQ3UU_neighbour-joining.tre
			if algo_run.newick == '' and algo_run.nwresult_path == '':
				msg['error'] = "Could not retrieve newick or network result."
				### status should be "failure" instead of "finished", but we won't change it in a status request			
				#return HttpResponse(json.dumps(msg, encoding = "utf8"))
				return HttpResponse(json.dumps(msg))
			else:	
				result = ""
				if algo_run.newick != '':
					msg['format'] = 'newick'
					try:
						with open(os.path.join(algo_media, algo_run.newick), 'r') as f:
							result = f.read()
					except:
						if algo_run.error_msg != '':
							msg['error'] = algo_run.error_msg
						else:
							msg['error'] = "Could not retrieve the newick."
					    ### status should be "failure" instead of "finished", but we won't change it in a status request
				if algo_run.nwresult_path != '':
					msg['format'] = 'network'
					try:
						with open(os.path.join(algo_media, algo_run.nwresult_path), 'r') as f:
							result = f.read()
					except:
						if algo_run.error_msg != '':
							msg['error'] = algo_run.error_msg
						else:
							msg['error'] = "Could not retrieve the network result."
					    ### status should be "failure" instead of "finished", but we won't change it in a status request

				msg['result'] = result
				msg['end_time'] = str(algo_run.end_time)
				#return HttpResponse(json.dumps(msg, encoding = "utf8"))
				return HttpResponse(json.dumps(msg))
		if algo_run.status == STATUS_CODES['failure']:
			msg['result'] = algo_run.error_msg  ### the result field shall contain the error info according to the white paper 
			msg['end_time'] = str(algo_run.end_time) 
			#return HttpResponse(json.dumps(msg, encoding = "utf8"))
			return HttpResponse(json.dumps(msg))

	
def processtest(request):
	#csv_file = "/Users/slinkola/STAM/data_sets/request4.json"
	#csv_file ="/home/stemweb/Stemweb/algorithm/fixtures/02_nj.json"	
	data_json = {"userid":"chrysaphi@gmail.com","parameters":{},"return_host":"stemmaweb.net:443","return_path":"/stemmaweb/stemweb/result","data":"_A_p1\t_A_p10\t_A_p11\t_A_p12\t_A_p13\t_A_p14\t_A_p15\t_A_p16\t_A_p2\t_A_p3\t_A_p4\t_A_p5\t_A_p6\t_A_p7\t_A_p8\t_A_p9\nIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\tIf\nvaccilation\tvacillation\tvacillation\tvacillation\tvacillation\tvacillation\tvacillation\tvacillation\tvacillation\tvacillation\tvaccilation\tvacillation\tvacillation\tvacillation\tvacillation\tvacillation\ndwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\tdwell\nwith\twith\twith\twith\twith\twith\twith\twith\twith\twith\twith\twith\twithin\twith\twith\twith\nthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\tthe\nheart\theart\theart\theart\theart\theart\theart\theart\theart\theat\theart\theart\theart\theat\theart\theat\n,\t\t\t\t\t\t\t\t\tof\t,\t\t\t\t\t\nthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul will\tthe soul" ,"textid":"B7D3FE44-B08E-11E1-A0A2-C59DFFF7791D"}

	csv = ""
	import codecs

	### PF: ToDo: Don't use codecs.open, use io.open instead.
	#with codecs.open(csv_file, 'r', encoding = 'utf8') as f:
	#with open(csv_file, 'r', encoding = 'utf8') as f:
	#	csv = f.read()
	

	msg = csv
	request = HttpRequest()
	request.method = 'POST'
	request.POST = msg
	request.content_type = "application/json"
	request.META = {}
	request.META['REMOTE_ADDR'] = '127.0.0.1'
	request.META['SERVER_PORT'] = 8000
	#execute_algorithm.external(json.loads(csv), 3, request)
	#return HttpResponse("ok")
	result = execute_algorithm.external(data_json, 11, request)
	return HttpResponse(result)


@csrf_exempt
def testresponse(request):
	if request.method == "POST":
		#print json.loads(request.body, encoding = "utf8")
		print(json.loads(request.data, encoding = "utf8"))		
		return HttpResponse("OK")
	return HttpResponse("No POST")

def testserver(request):
	ret = utils.validate_server(request)
	return HttpResponse(ret[0])
	

	

