#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django import forms
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.models import AnonymousUser

from Stemweb.third_party_apps.recaptcha_works.fields import RecaptchaField
from models import InputFile

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
	''' Subclass of ModelChoiceField which takes one additional required 
	argument 'user' and populates queryset with that users InputFile's if user 
	is authenticated.
	
	Returns None if user is not authenticated or is AnonymousUser.
	
	Validate-method is overrided to check if the given pk of InputFile belongs
	to the user given in __init__. '''
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', AnonymousUser)
		
                # omit user checks due to user registration problems
		#kwargs['queryset'] = EmptyQuerySet()
		#if self.user is not AnonymousUser: 
		#	if self.user.is_authenticated():
		kwargs['queryset'] = InputFile.objects.filter(user__exact = self.user)		
		#else:
		'''
						TODO: add AnonymousUser logic here
						ATM tests suppose that AnonymousUsers don't have any 
						input files.
		'''	
		super(InputFileChoiceField, self).__init__(*args, **kwargs)
	
	def to_python(self, value):
		if not value: return None
		
		try: value = int(value)
		except: raise forms.ValidationError('Needs a proper int value.')
		
		return value
	
	def validate(self, value):
		if not value: raise forms.ValidationError('No input file given. ')
		
		if self.user is not AnonymousUser:
			if self.user.is_authenticated():
				f = InputFile.objects.get_or_none(pk__exact = value)
				if f is None:
					raise forms.ValidationError('Requested input file was not found from database.')
				if f.user.id is not self.user.id:
					raise forms.ValidationError('You are not owner of this file.')
				else:
					self.input_file = f
			else:
				raise forms.ValidationError('You are not authenticated.')	
		else:
			raise forms.ValidationError('Anonymous users cannot currently use algorithms.')
		
	def clean(self, *args, **kwargs):
		cleaned_data = super(InputFileChoiceField, self).clean(*args, **kwargs)
		cleaned_data = self.input_file
		return cleaned_data
				
		
		
