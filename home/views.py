#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, loader


def home(request): 
    ''' 
    	Mother of all views.
    	
    	TODO: put user's recent activities into left tab when user is logged in.
    '''   
    c = RequestContext(request)
    t = loader.get_template('home.html')  
    return HttpResponse(t.render(c))
    

def server_error(request):
    return HttpResponse('Internal Server Error: We are sorry, but we could not handle your request.')
    
def script_failure(request):
    return HttpResponse('Script\'s run was failure for unknown reason.')    
    