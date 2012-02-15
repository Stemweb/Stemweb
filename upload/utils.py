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
    uppath = os.path.join(uppath, instance.file_ext)
    uppath = os.path.join(uppath, id_generator())
    uppath = os.path.join(uppath, filename)
    instance.path = os.path.join(settings.MEDIA_ROOT, uppath)
    
    return uppath

# 	Semiunique ID generator -- copypaste code.
#	Generates random string to be added for example
#	to output folders of R-script's output.
#
#	Source:
# 	http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
#
#	params:
#		size - length of the random string. Default 8.
#		chars - set of chars from which the string is created
#
#	Returns created string
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

