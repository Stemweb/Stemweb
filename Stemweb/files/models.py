#!/usr/bin/env python
# -*- coding: utf-8 -*-

# All database models (ie. tables). Django creates
# these tables with "python manage.py syncdb" -command.

from django.db import models
from django.utils.encoding import smart_str
from . import utils

class GetOrNoneManager(models.Manager):
	''' Adds get_or_none method to objects. '''
	def get_or_none(self, **kwargs):
		try:
			return self.get(**kwargs)
		except self.model.DoesNotExist:
			return None

class InputFile(models.Model):
	''' Basic table for all input files to any of the scripts. 
	'''
	upload_time = models.DateTimeField(auto_now_add = True) # Uploading time 
	last_access = models.DateTimeField(auto_now = True)
	name = models.CharField(max_length = 80)        # Base name of the input file
	extension = models.CharField(max_length = 15, default = 'nex')   # File extension
	file = models.FileField(upload_to = utils.upload_path)
	external = models.BooleanField(default = False)

	class Meta:
		ordering = ['name', 'extension', '-last_access']

	def __str__(self):
		return smart_str('%s uploaded: %s' % (self.file, self.upload_time.strftime('%d.%m.%y %H:%M')))
	
	objects = GetOrNoneManager()
