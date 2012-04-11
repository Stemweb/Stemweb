#!/usr/bin/env python
# -*- coding: utf-8 -*-

# All database models (ie. tables). Django creates
# these tables with "python manage.py syncdb" -command.

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
import utils

# Basic table for all input files to any of the scripts.   
class InputFile(models.Model):

	user = models.ForeignKey(User)                  # User who uploaded the file
	upload_time = models.DateTimeField(auto_now_add = True) # Uploading time 
	last_access = models.DateTimeField(auto_now = True)
	extension = models.CharField(max_length = 10, default = 'nex')   # File extension
	name = models.CharField(max_length = 80)        # Base name of the input file
	file = models.FileField(upload_to = utils.upload_path)
	path = models.CharField(max_length = 200, blank = True, default = file.get_directory_name())       # Absolute file path to this file

	class Meta:
		ordering = ['name', 'extension', '-last_access']

	def __str__(self):
		return smart_str('%s uploaded: %s' % (self.name, self.upload_time.strftime('%d.%m.%y %H:%M')))