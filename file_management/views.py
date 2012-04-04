from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from Stemweb import upload
import os
from Stemweb import settings
from Stemweb.django_proto.models import InputFiles

@login_required
def users_files(request):
    
    # Get all files that user has uploaded.
    user_files = InputFiles.objects.filter(user = request.user)
    context = RequestContext(request, { 'files': user_files})
    return render_to_response('file_management_users_files.html', context)

@login_required
def index(request):
    context = RequestContext(request)
    return render_to_response('file_management_index.html', context)
    
@login_required
def base(request):
    user_files = InputFiles.objects.filter(user = request.user)
    context = RequestContext(request, { 'files': user_files})
    return render_to_response('file_management_base.html', context)
    
    