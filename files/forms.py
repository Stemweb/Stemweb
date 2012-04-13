#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from Stemweb.third_party_apps.recaptcha_works.fields import RecaptchaField
import os

def validate_upload_file(FileField):
	'''
		Simple validator that check's that FileField's basename is no more than 
		30 characters long.
	'''
	filename = os.path.basename(FileField.name)
	if len(filename) > 30:
		raise forms.ValidationError('File\'s name %s is too long. Only 30 characters allowed.' % (FileField.name))


class UploadFile(forms.Form):
	'''
		Simple form to select a file from local system with recaptcha validation.
	'''
	upfile = forms.FileField(label='', 
                             max_length=30, 
                             widget=forms.ClearableFileInput(attrs={'size': 23, 'class': 'file_input'}))
	#captcha = RecaptchaField(label='', required=True)
