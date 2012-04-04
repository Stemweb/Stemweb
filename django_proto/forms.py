#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from recaptcha_works.fields import RecaptchaField
from Stemweb.algorithms.forms import is_positive_integer
import os

"""
				FIELD VALIDATORS
"""

# Simple validator that check's that FileField's basename 
# is no more than 30 characters long.
def validate_upload_file(FileField):
    filename = os.path.basename(FileField.name)
    if len(filename) > 30:
        raise forms.ValidationError('File\'s name %s is too long. Only 30 characters allowed.' % (FileField.name))


"""
				FORMS 
"""

# Simple form to select a file from local system.
class Upload_file(forms.Form):
    upfile = forms.FileField(label='', 
                             max_length=30, 
                             widget=forms.ClearableFileInput(attrs={'size': 30, 'class': 'file_input'}))
    
    captcha = RecaptchaField(label='', required=True)

# Form to choose runsemf81 run's parameters.    
class Run_file(forms.Form):

	itermaxin = forms.IntegerField(label = 'Iteration max', validators = [is_positive_integer])
	runmax = forms.IntegerField(label = '\"Parallel\" runs', validators = [is_positive_integer])
    