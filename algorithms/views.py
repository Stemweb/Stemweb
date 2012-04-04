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
from models import Algorithm

def base(request):
	algorithms = Algorithm.objects.all()
	print len(algorithms)
	c = RequestContext(request, {"all_algorithms" : algorithms})
	t = loader.get_template('algorithms_base.html')  
	return render_to_response("algorithms_base.html", c)
	