from django import forms
from django.contrib.auth.models import User, AnonymousUser

from Stemweb.files.models import InputFile
from .settings import ARG_VALUE_FIELD_TYPE_KEYS, ARG_VALUE_FIELD_TYPE_VALIDATORS
import validators as val

field_types =  {'positive_integer': forms.IntegerField(),
				'integer': forms.IntegerField(),
				'float': forms.FloatField(),
			   	'string': forms.CharField(),
			   	'input_file': forms.ModelChoiceField(label = None, queryset = None),
			   	'boolean': forms.BooleanField() }
		
field_validators = {'positive_integer': [val.is_positive_integer],
					'integer': [],
					'float': [],
				   	'string': [],
				   	'input_file': [],
				   	'boolean': [] }

class DynamicArgs(forms.Form):
	
	def __init__(self, *args, **kwargs):
		'''
			Build dynamic algorithm's arguments form.
			
			user:	User who is currently active in this session. Only this 
					user's files will be shown as possible input files.
					
			arguments:	'args' field from instance of Algorithm model.
			
			post:	request.POST to populate form fields so that is_valid() 
					can be called. Don't use this if you expect user to 
					populate the fields.
		'''
		user = kwargs.pop('user', AnonymousUser)
		post = kwargs.pop('post', None)
		arguments = kwargs.pop('arguments', None)
		
		super(forms.Form, self).__init__(*args, **kwargs)
		
		ftypes =  ARG_VALUE_FIELD_TYPE_KEYS
		field_validators = ARG_VALUE_FIELD_TYPE_VALIDATORS
		
		for arg in arguments.all():
			key, value, name = arg.key, arg.value, arg.verbose_name
			kwargs = {'label': name, 'validators': field_validators[value]}
			if value == 'boolean': kwargs['required'] = False
			if value == 'input_file':
				''' Input File fields are populated dynamically based on user. '''
				if user.is_authenticated():
					kwargs['queryset'] = InputFile.objects.filter(user__exact = user)		
					self.fields[key] = ftypes[value](**kwargs)
					'''
						TODO: add AnonymousUser logic here
					'''	
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
			
				
		
		
				

	