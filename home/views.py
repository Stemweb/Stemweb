#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.template import RequestContext, loader
from Stemweb.files.models import InputFile
from Stemweb.algorithms.models import AlgorithmRun

def get_recent_activities(user):
	delta = 14
	ra = []
	uploaded = InputFile.objects.filter(user__exact = user, upload_time__gte = datetime.now()-timedelta(days=delta))
	started_runs = AlgorithmRun.objects.filter(user__exact = user, start_time__gte = datetime.now()-timedelta(days=delta))
	ended_runs = AlgorithmRun.objects.filter(user__exact = user, end_time__gte = datetime.now()-timedelta(days=delta))
	
	if len(uploaded) is 0 and len(started_runs) is 0 and len(ended_runs) is 0:
		return None
	
	for u in uploaded: 
		ra.append({'time': u.upload_time, 'message': "Uploaded file %s" % (u.name), 'url': '/files/%s' % (u.id)})
	for s in started_runs: 
		ra.append({'time': s.start_time, 'message': "Started %s with %s" % (s.algorithm.name, s.input_file.name), 'url': '/algorithms/results/%s' % (s.id)})
	for s in ended_runs: 
		ra.append({'time': s.end_time, 'message': "%s run with %s ended" % (s.algorithm.name, s.input_file.name), 'url': '/algorithms/results/%s' % (s.id)})
	ra = sorted(ra, key = lambda a: a['time'], reverse = True)
	
	return ra

def home(request): 
	''' 
    	Mother of all views.
    	
    	TODO: put user's recent activities into left tab when user is logged in.
    '''  
	recent_activities = None 
	if request.user.is_authenticated():
		recent_activities = get_recent_activities(request.user)
	
	c = RequestContext(request, {'recent_activities': recent_activities})
	t = loader.get_template('home.html')  
	return HttpResponse(t.render(c))


def server_error(request):
	return HttpResponse('Internal Server Error: We are sorry, but we could not handle your request.')

def script_failure(request):
	return HttpResponse('Script\'s run was failure for unknown reason.')    
