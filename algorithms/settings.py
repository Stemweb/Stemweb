'''
	Settings for algorithms-application. 
'''
import os

from django import forms
from Stemweb.settings import SITE_ROOT

from .semstem import Semstem
from .neighbour_joining.nj_class import NJ
import validators

# How many runs can be active by one user.
USER_RUNS = 2
# How many runs can be active at all times.
ALL_RUNS = 8

THREADS = {}

ALGORITHMS_CALLING_DICT = { 
	'1': { 
		'callable': Semstem,	
		'source': os.path.join(SITE_ROOT, 'algorithms/semsep_stop_len/allunilen.r'),
	},
	'2': {
		'callable': None,
		'source': None,
	},
	'3': {
		'callable': NJ,
	}
}

'''
	Choices for AlgorithmArg value types. These must be 2-tuples of strings. 
	Check django's documentation for choice fields.
'''
ARG_VALUE_CHOICES = [
	('positive_integer', 'Positive Integer'),
	('integer', 'Integer'),
	('float', 'Float'),
	('boolean', 'Boolean'),
	('string', 'String'),
	('input_file', 'Input File (foreign key to InputFiles model)')
]

'''
	AlgorithmArg value types. Each key is a string from ARG_VALUE_CHOICES first
	index and value is field type for that key.
'''
ARG_VALUE_FIELD_TYPE_KEYS =  {
	'positive_integer': forms.IntegerField,
	'integer': forms.IntegerField,
	'float': forms.FloatField,
	'string': forms.CharField,
	'input_file': forms.ModelChoiceField,
	'boolean': forms.BooleanField
}

'''
	AlrgorithmArg value field validators. Each key is a string from 
	ARG_VALUE_CHOICES first index and value is a list of validators used for
	that key.
'''
ARG_VALUE_FIELD_TYPE_VALIDATORS = {
	'positive_integer': [validators.is_positive_integer],
	'integer': [],
	'float': [],
   	'string': [],
   	'input_file': [],
   	'boolean': [] 
}