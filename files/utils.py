#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Utility methods for uploaded files. 

import os
import string
import random
import Stemweb.settings as settings

#    Creates file_field and abs_path for Input_files instances.
#    This method is called anytime Input_files object is created
#    and it uploaded files associated with file_field into abs_path.
#
#    (Though it actually creates first the object into path relative 
#    to MEDIA_ROOT but abs_path is created just by joinin MEDIA_ROOT
#    with this upload path.)
def upload_path(instance, filename):
	uppath = os.path.join('users', instance.user.username)
	uppath = os.path.join(uppath, 'files')
	uppath = os.path.join(uppath, instance.extension)
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

