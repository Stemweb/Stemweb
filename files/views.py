import logging

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from Stemweb.third_party_apps.recaptcha_works.decorators import fix_recaptcha_remote_ip

from models import InputFile
from forms import UploadFile

@login_required
def details(request, file_id, form = None):
	'''
 		Detail view of one of the user's files.
	'''
	details_file = InputFile.objects.get(pk = file_id)
	if details_file.user != request.user:
		logger = logging.getLogger('stemweb.auth')
		logger.warning('Request user %s tried to access file %s which is owned by %s.' % (request.user, details_file.id, details_file.user))
		return HttpResponseRedirect('/server_error')
	
	if form is None or form.__class__ != UploadFile:
		form = UploadFile
	
	user_files = InputFile.objects.filter(user = request.user)
	context = RequestContext(request, { 'user_files': user_files, 'file': details_file, 'form': form})
	return render_to_response('files_details.html', context)

@login_required
def base(request, form = None):
	'''
		Base view for files-subpage.
	'''
	if form is None or form.__class__ != UploadFile:
		form = UploadFile
	
	user_files = InputFile.objects.filter(user = request.user)
	context = RequestContext(request, { 'user_files': user_files, 'form': form })
	return render_to_response('files_base.html', context)


@login_required
@fix_recaptcha_remote_ip
def upload(request):
	'''
		Handles upload form. If gets POST-data will upload and save file in 
		server and then redirect to that file's subpage.
	'''
	if request.method == 'POST':
		form = UploadFile(request.POST, request.FILES)
		if form.is_valid():
			f = request.FILES['upfile']
			input_file = InputFile(name = f.name, 
                                   user = request.user, 
                                   file = f)  
			input_file.save() # Save to be sure input_file.id is created                                      
			return HttpResponseRedirect('/files/%s' % (input_file.id))
		else:
			form = UploadFile()
	context = RequestContext(request)            
	return render_to_response('/files/',
                              { 'form': form },
                              context_instance=context)
	
	