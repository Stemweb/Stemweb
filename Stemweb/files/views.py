import logging

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from models import InputFile
from forms import UploadFile

def details(request, file_id, form = None):
	'''
 		Detail view of one of the files.
	'''
	details_file = InputFile.objects.get(pk = file_id)
	
	if form is None or form.__class__ != UploadFile:
		form = UploadFile
	
	#allfiles = InputFile.objects.all()
	#context = RequestContext(request, {'file': details_file, 'form': form})
	#return render_to_response('files_details.html', context.flatten())
        return render_to_response('files_details.html',  {'file': details_file, 'form': form}) 

def base(request, form = None):
	'''
		Base view for files-subpage.
	'''
	if form is None or form.__class__ != UploadFile:
		form = UploadFile
	
	allfiles = InputFile.objects.all()
	#context = RequestContext(request, { 'all_files': allfiles, 'form': form })
	#return render_to_response('files_base.html', context.flatten())
	return render_to_response('files_base.html', { 'all_files': allfiles, 'form': form })


def upload(request):
	'''
		Handles upload form. If gets POST-data will upload and save file in 
		server and then redirect to that file's subpage.
	'''
	if request.method == 'POST':
		form = UploadFile(request.POST, request.FILES)
		if form.is_valid():
			f = request.FILES['upfile']
			input_file = InputFile(name = f.name, file = f) 
			input_file.extension = (f.name).rsplit(".", 1)[1]
			input_file.save() # Save to be sure input_file.id is created                                      
			return HttpResponseRedirect('/files/%s' % (input_file.id))
		else:
			form = UploadFile()
	#context = RequestContext(request) 
	return render_to_response('/files/',
                              { 'form': form },
                              #context_instance=context)
                              request = request)	
	
