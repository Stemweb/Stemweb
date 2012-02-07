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
import os
import pyper_runs_yuan

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
                return HttpResponseRedirect('/runparams/%s' % (input_file.id))    # And redirect to run that file
            else:
                return HttpResponseRedirect('/server_error')
                
    else:
        form = Upload_file()
        return HttpResponseRedirect('/home')
    
# Handles running of one file.
def runparams(request, file_id):
                 
    #last_runs = models.Script_runs.objects.get(input_file = file_id)
    form = Run_file()
    input_file = models.Input_files.objects.get(id = file_id)
    all_runs = models.Script_runs.objects.filter(input_file__exact = input_file)
    context = dict({'input_file': input_file, 'form': form, 'all_runs': all_runs})
    c = RequestContext(request, context)
    return render_to_response('runparams.html', c)

def run(request, file_id):
    
    if request.method == 'POST':
        form = Run_file(request.POST)
        if form.is_valid():
            imax = form.cleaned_data['itermaxin']
            rmax = form.cleaned_data['runmax']
            ifile = models.Input_files.objects.get(id = file_id)
            srun = models.Script_runs(input_file = ifile, itermax = imax, runmax = rmax, res_folder = '', res_pic = '')
            srun.save()
            fpath = srun.input_file.path
            run_id = srun.id
            fpath = file_operations.build_runpath(fpath, run_id)
            logpath = os.path.join(fpath, 'run_log.txt')
            log_file = open(logpath, 'w')
            log_file.writelines(['Input file path: ', srun.input_file.path, '\n', 
                                 'Iteration max: ', srun.itermax, '\n',
                                 'Simultaneous runs: ', srun.runmax, '\n',
                                 'Run path: ', fpath, '\n'])
            log_file.close()
            if (fpath is not -1): 
                srun.res_folder = fpath
                srun.save()
                run_args = dict({'itermaxin' : int(srun.itermax), 
                                 'runmax'    : int(srun.runmax), 
                                 'infile'    : srun.input_file.path, 
                                 'outfolder' : srun.res_folder})
                ret_val = pyper_runs_yuan.runsemf81(run_args)
                log_file = open(logpath, 'a')
                log_file.write('Output folder is: %s \n' % (srun.res_folder))
                log_file.write('runsemf81 return value was: %d \n' % (ret_val))
                log_file.close()
                if ret_val == -1:
                    srun.delete();
                    HttpResponseRedirect('/script_failure') 
                else:    
                    srun.res_pic = 'besttree.png'
                    srun.save()
                    return HttpResponseRedirect('/results/%s/%s' % (srun.input_file.id, srun.id))
            else:
                return HttpResponseRedirect('/server_error')
        else: 
            return HttpResponseRedirect('/server_error')
    else:
        return HttpResponse('No post data')
    
def results(request, file_id, run_id):
    input_file = models.Input_files.objects.get(id = file_id)
    srun = models.Script_runs.objects.get(id = run_id)
    context = dict({'input_file': input_file, 'srun': srun})
    c = RequestContext(request, context)
    return render_to_response('results.html', c)

def server_error(request):
    return HttpResponse('Internal Server Error: We are sorry, but we could not handle your request.')
    
def script_failure(request):
    return HttpResponse('Script\'s run was failure for unknown reason.')    
    
    