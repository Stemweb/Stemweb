'''
Created on Mar 28, 2012

@author: slinkola
'''
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from forms import SemsepArgs
from models import Algorithm, AlgorithmRuns

def base(request):
	algorithms = Algorithm.objects.all()
	c = RequestContext(request, {"all_algorithms" : algorithms}) 
	return render_to_response("algorithms_base.html", c)

def details(request, algo_id):
	algorithm = Algorithm.objects.get(id = algo_id)
	algorithm_runs = None
	if request.user.is_authenticated():
		algorithm_runs = AlgorithmRuns.objects.filter(user = request.user, algorithm = algo_id )
	c = RequestContext(request, {"algorithm" : algorithm, 
								"algorithm_runs" : algorithm_runs,
								"all_algorithms": Algorithm.objects.all()})
	return render_to_response("algorithms_details.html", c)