import logging

from django import forms
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.models import User, AnonymousUser
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
			
			user:	User who is currently active in this session. Only this 
					user's files will be shown as possible input files.
					
			arguments:	'args' field from instance of Algorithm model.
			
			post:	request.POST to populate form fields so that is_valid() 
					can be called. Don't use this if you expect user to 
					populate the fields.
		'''
		self.user = kwargs.pop('user', AnonymousUser)
		post = kwargs.pop('post', None)
		arguments = kwargs.pop('arguments', None)
		
		super(forms.Form, self).__init__(*args, **kwargs)
		
		# We need to keep these in mind to check that all of them will be owned
		# by self.user when form is validated.
		self.input_files = []
		
		for arg in arguments.all():
			key, value, name = arg.key, arg.value, arg.name
			kwargs = {'label': name, 'validators': field_validators[value]}
			if value == 'boolean': kwargs['required'] = False
			if value == 'input_file': 
				kwargs['user'] = self.user
				field = ftypes[value](**kwargs)
				#print "%s %s" % (self.user, len(field.queryset))
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
			for key in post.keys():
				self.data[key] = post[key]
			self.is_bound = True
	
	'''		
	def clean(self):
		Overrided clean-method to verify that all input files are owned by
		self.user. 
		
		cleaned_data = super(DynamicArgs, self).clean()
		to_remove = []
		
		for key in self.input_files:
			if key not in cleaned_data: to_remove.append(key)
		
		for key in to_remove:
			self.input_files.remove(key)
		del to_remove
		
		for key in self.input_files:
			input_file = get_object_or_404(InputFile, pk__exact = cleaned_data[key])
			if self.user is not input_file.user:
				logger = logging.getLogger('stemweb.algorithm_run')
				logger.warning("Could not clean DynamicArgs-form because self.user %s was not InputFile.user %s" % (self.user, input_file.user))
				raise forms.ValidationError("File is owned by other user.")
			else: 
				cleaned_data[key] = input_file
		
		return cleaned_data
		
		return super(DynamicArgs, self).clean()
	'''		
			
				
		
		
				

	
