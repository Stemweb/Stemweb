import logging

from django import forms
from django.db.models.query import EmptyQuerySet
from django.shortcuts import get_object_or_404

from Stemweb.files.models import InputFile
from .settings import ARG_VALUE_FIELD_TYPE_KEYS as ftypes
from .settings import ARG_VALUE_FIELD_TYPE_VALIDATORS as field_validators

class DynamicArgs(forms.Form):
	
	def __init__(self, *args, **kwargs):
		'''
			Build algorithm's arguments form dynamically based on given arguments.
			This form is shown in browser when user wants to do a new run for 
			certain algorithm.
			
			arguments:	'args' field from instance of Algorithm model.
			
			post:	request.POST to populate form fields so that is_valid() 
					can be called. Don't use this if you expect user to 
					populate the fields.
		'''
		post = kwargs.pop('post', None)
		arguments = kwargs.pop('arguments', None)
		
		super(forms.Form, self).__init__(*args, **kwargs)
		
		self.input_files = []
		
		for arg in arguments.all():
			key, value, name = arg.key, arg.value, arg.name
			kwargs = {'label': name, 'validators': field_validators[value]}
			if value == 'boolean': kwargs['required'] = False
			if value == 'input_file': 
				field = ftypes[value](**kwargs)
				#print "%s" % ( len(field.queryset))
				#if field is not EmptyQuerySet():         ## raises TypeError("EmptyQuerySet can't be instantiated")
				if field:                                 ## using simpler check instead   
					self.input_files.append(key)
					self.fields[key] = field
			else: 			
				self.fields[key] = ftypes[value](**kwargs)
		'''
			If there is request, we change form's data to correspond request's
			key values.
		'''				
		if post is not None:
			for key in list(post.keys()):
				self.data[key] = post[key]
			self.is_bound = True
	
