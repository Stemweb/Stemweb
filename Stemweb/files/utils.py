#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Utility methods for uploaded files. 

import os
import string
import random

from django.conf import settings

def upload_path(instance, filename):
	''' Returns upload path where InputFile -instance with filename should be 
	    uploaded.
	'''
	uppath = os.path.join(uppath, 'files')
	uppath = os.path.join(uppath, filename.rsplit('.', 1)[1]) # extension
	uppath = os.path.join(uppath, filename)
	instance.path = os.path.join(settings.MEDIA_ROOT, uppath)
	return uppath

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
	''' Semiunique ID generator.
		
		size:	length of the random string. Default 8.
		chars:	set of chars from which the string is created

		Returns random string.
	'''
	return ''.join(random.choice(chars) for x in range(size))

