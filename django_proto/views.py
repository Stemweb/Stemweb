#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from recaptcha_works.decorators import fix_recaptcha_remote_ip

from forms import Upload_file
from Stemweb.algorithms.forms import SemsepArgs
from Stemweb.algorithms.models import AlgorithmRuns, Algorithm
from forms import Run_file
import models
import handler
import run_scripts
from Stemweb import settings

# Default view of the prototype.
def home(request): 
           
    files = models.InputFiles.objects.all()
    form = Upload_file()
    c = RequestContext(request, {'form': form, 'files': files})
    t = loader.get_template('home.html')  
    return HttpResponse(t.render(c))
    
# Handles upload form. If gets POST-data will upload and save file 
# in server and then redirect to view to run_script that file.
@login_required
@fix_recaptcha_remote_ip
def upload(request):
    if request.method == 'POST':
        form = Upload_file(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['upfile']
            input_file = models.InputFiles(name = f.name, 
                                            user = request.user, 
                                            file_field = f)  
            
            input_file.save() # Save to be sure input_file.id is created                                      
            return HttpResponseRedirect('/runparams/%s' % (input_file.id))    # And redirect to run_script that file
    else:
        form = Upload_file()
            
    context = RequestContext(request)            
    return render_to_response('home.html',
                              { 'form': form },
                              context_instance=context)
    
# Handles running of one file.
def runparams(request, file_id):
                
    form = SemsepArgs(user = request.user)
    ifile = models.InputFiles.objects.get(id = file_id)
    all_runs = AlgorithmRuns.objects.filter(input_file__exact = ifile, user__exact = request.user)
    context = dict({'input_file': ifile, 'form': form, 'all_runs': all_runs})
    c = RequestContext(request, context)
    return render_to_response('runparams.html', c)

@login_required
#@user_passes_test()
def run_script(request, file_id):
    
    if request.method == 'POST':
        form = SemsepArgs(request.POST)
        if form.is_valid():
        	imax = form.cleaned_data['itermaxin']
        	rmax = form.cleaned_data['runmax']
        	ifile = models.InputFiles.objects.get(id = form.cleaned_data['infile'])
        	run_folder = handler.build_run_folder(request.user, ifile.id, 'f81')
        	
        	if run_folder == -1:
        		return HttpResponseRedirect('/server_error')
        	abs_folder = os.path.join(settings.MEDIA_ROOT, run_folder) 
        	run_args = dict({'itermaxin' : int(imax), 
                             'runmax'    : int(rmax), 
                             'infile'    : ifile.path, 
                             'outfolder' : abs_folder})
        	
        	run_scripts.f81(run_args)  
        	img = os.path.join(run_folder, 'besttree.png')
        	srun = AlgorithmRuns.objects.create(input_file = ifile,
													 algorithm = Algorithm.objects.get(id = 1), 
													 user = request.user,
                                                     itermax = imax, 
                                                     runmax = rmax, 
                                                     folder = abs_folder, 
                                                     image = img)
        	srun.save()
        	return HttpResponseRedirect('/results/%s/%s' % (srun.input_file.id, srun.id))
    else:
        form = SemsepArgs(user = request.user)
     	ifile = models.InputFiles.objects.get(id = file_id)
     	all_runs = AlgorithmRuns.objects.filter(input_file__exact = ifile)
	
	c = RequestContext(request)
	return render_to_response('runparams.html', 
							{'input_file': ifile, 'form': form, 'all_runs': all_runs}, 
							context_instance = c)    
    
def results(request, file_id, run_id):
    input_file = models.InputFiles.objects.get(id = file_id)
    srun = AlgorithmRuns.objects.get(id = run_id)
    context = dict({'input_file': input_file, 'srun': srun})
    c = RequestContext(request, context)
    return render_to_response('results.html', c)

def server_error(request):
    return HttpResponse('Internal Server Error: We are sorry, but we could not handle your request.')
    
def script_failure(request):
    return HttpResponse('Script\'s run was failure for unknown reason.')    
    
    