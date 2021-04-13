#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django import forms
from django.db.models.query import EmptyQuerySet

from .models import InputFile

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


class InputFileChoiceField(forms.ModelChoiceField):
	''' Subclass of ModelChoiceField which populates queryset with InputFiles
        '''	
	
	def __init__(self, *args, **kwargs):
		kwargs['queryset'] = InputFile.objects.all()		
		super(InputFileChoiceField, self).__init__(*args, **kwargs)
	
	def to_python(self, value):
		if not value: return None
		
		try: value = int(value)
		except: raise forms.ValidationError('Needs a proper int value.')
		
		return value
	
	def validate(self, value):
		if not value: raise forms.ValidationError('No input file given. ')
		
		f = InputFile.objects.get_or_none(pk__exact = value)
		if f is None:
			raise forms.ValidationError('Requested input file was not found in  database.')
		self.input_file = f
		
	def clean(self, *args, **kwargs):
		cleaned_data = super(InputFileChoiceField, self).clean(*args, **kwargs)
		cleaned_data = self.input_file
		return cleaned_data
				
		
		
