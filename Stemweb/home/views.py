#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.template import RequestContext, loader
from Stemweb.files.models import InputFile
from Stemweb.algorithms.models import AlgorithmRun

def get_recent_activities():
	delta = 14
	ra = []
	uploaded = InputFile.objects.filter(upload_time__gte = datetime.now()-timedelta(days=delta))
	started_runs = AlgorithmRun.objects.filter(start_time__gte = datetime.now()-timedelta(days=delta))
	ended_runs = AlgorithmRun.objects.filter(end_time__gte = datetime.now()-timedelta(days=delta))
	
	if len(uploaded) == 0 and len(started_runs) == 0 and len(ended_runs) == 0:
		return None
	
	for u in uploaded: 
		ra.append({'time': u.upload_time, 'message': "Uploaded file %s" %\
				 (u.name), 'url': '/files/%s' % (u.id)})
	for s in started_runs: 
		ra.append({'time': s.start_time, 'message': "Started %s with %s" %\
				 (s.algorithm.name, s.input_file.name), 'url': '/algorithms/results/%s' % (s.id)})
	for s in ended_runs: 
		ra.append({'time': s.end_time, 'message': "%s run with %s ended" %\
				 (s.algorithm.name, s.input_file.name), 'url': '/algorithms/results/%s' % (s.id)})
	ra = sorted(ra, key = lambda a: a['time'], reverse = True)
	
	return ra

def home(request): 
	''' Mother of all views. '''  
	recent_activities = None 
	recent_activities = get_recent_activities()
	
	#c = RequestContext(request, {'recent_activities': recent_activities})
	t = loader.get_template('home.html')  
	#return HttpResponse(t.render(c))
	# In Django 1.8+, the template's render method takes a dictionary for the context parameter. Support for passing a Context instance is deprecated, and gives an error in Django 1.10+.
	# hence let us just use a regular dict instead of a Context instance:
	#return HttpResponse(t.render(c.flatten()))
	return HttpResponse(t.render({'recent_activities': recent_activities}))

def server_error(request):
	return HttpResponse('Internal Server Error: We are sorry, but we could not handle your request.')

def script_failure(request):
	return HttpResponse('Script\'s run failed for unknown reason.')    
