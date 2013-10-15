'''
	Settings for algorithms-application. 
'''
from django import forms

from Stemweb.files import forms as files_forms

#from .semstem.semstem import Semstem
from .semstem.semstemprob import Semstem
#from .neighbour_net.neighbornet_class import NN
from .neighbour_joining.njc import NJ
from .rhm.binary_sankoff import RHM
import validators
import  lsettings

URL_PREFIX = 'algorithms'

'''
	Dictionary mapping Algorithm models' ids to dictionaries which contain 
	atleast 'callable' keyword and possible other entries. 'callable' should 
	refer to actual subclass of AlgorithmTask and other entries are passed 
	inside run_args dictionary to that callable.
'''
ALGORITHMS_CALLING_DICT = { 
	'1': { 
		'callable': Semstem,	
	},
	'2': {
		'callable': RHM,
	},
	'3': {
		'callable': NJ,
	},
#	'4': {
#		'callable': NN,
#	},	
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
	'input_file': files_forms.InputFileChoiceField,
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

TRUSTED_SERVERS = lsettings.TRUSTED_SERVERS

#ALGORITHM_RUN_STATES = 