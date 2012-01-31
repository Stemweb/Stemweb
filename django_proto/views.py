#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from forms import Upload_file
from forms import Run_file
import models
import file_operations
from semsep import pyper_runs_yuan

# Default view of the prototype.
def home(request): 
           
    files = models.Input_files.objects.all()
    form = Upload_file()
    c = RequestContext(request, {'form': form, 'files': files})
    t = loader.get_template('home.html')  
    return HttpResponse(t.render(c))
    
# Handles upload form. If gets POST-data will upload and save file 
# in server and then redirect to view to run that file.
def upload(request):
    if request.method == 'POST':
        form = Upload_file(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['upfile']
            input_file = models.Input_files(name = f.name, path = '', )   # Add file to db to create id
            input_file.save()
            fpath = file_operations.build_filepath(f.name, input_file.id)    # Create path with respect to id
            if (fpath is not -1):                      
                input_file.path = fpath
                fpath = file_operations.handle_uploaded_file(f, fpath)      # Upload the file created path
                input_file.save()
                return HttpResponseRedirect('runparams/%s' % (input_file.id))    # And redirect to run that file
            else:
                return HttpResponseRedirect('server_error')
                
    else:
        form = Upload_file()
        return HttpResponseRedirect('/home')
    
# Handles running of one file.
def runparams(request, file_id):
                 
    #last_runs = models.R_runs.objects.get(input_file = file_id)
    form = Run_file()
    input_file = models.Input_files.objects.get(id = file_id)
    context = dict({'input_file': input_file, 'form': form})
    c = RequestContext(request, context)
    return render_to_response('runparams.html', c)

def run(request, file_id):
    
    if request.method == 'POST':
        form = Run_file(request.POST)
        if form.is_valid():
            imax = form.cleaned_data['itermaxin']
            rmax = form.cleaned_data['runmax']
            ifile = models.Input_files.objects.get(id = file_id)
            r_run = models.R_runs(input_file = ifile, itermax = imax, runmax = rmax, res_folder = '', res_pic = '')
            r_run.save()
            fpath = r_run.input_file.path
            run_id = r_run.id
            fpath = file_operations.build_runpath(fpath, run_id)
            if (fpath is not -1): 
                r_run.res_folder = fpath
                r_run.save()
                run_args = dict({'itermaxin' : r_run.itermax, 
                                 'runmax'    : r_run.runmax, 
                                 'infile'    : r_run.input_file.path, 
                                 'outfolder' : r_run.res_folder})
                pyper_runs_yuan.runsemf81(run_args)
                return HttpResponseRedirect('/results/%s/%s' % (r_run.input_file.id, r_run.id))
            else:
                return HttpResponseRedirect('/server_error')
        else: 
            return HttpResponseRedirect('/server_error')
    else:
        return HttpResponse('No post data')
    
def results(request, file_id, run_id):
    input_file = models.Input_files.objects.get(id = file_id)
    r_run = models.R_runs.objects.get(id = run_id)
    context = dict({'input_file': input_file, 'r_run': r_run})
    c = RequestContext(request, context)
    return render_to_response('results.html', c)

def server_error(request):
    return HttpResponse('Internal Server Error: We are sorry, but we could not handle your request.')
    