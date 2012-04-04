'''
	Forms for all algorithms' input arguments. 
'''

from django import forms
from django.contrib.auth.models import AnonymousUser
from Stemweb.django_proto.models import InputFiles



def is_positive_integer(IntegerField):
	if IntegerField <= 0:
		raise forms.ValidationError("Value should be positive integer.")
	
	
class SemsepArgs(forms.Form):
	'''
		Form for semsep algorithm's arguments. 
	'''
	itermaxin = forms.IntegerField(label = 'Iteration max', validators = [is_positive_integer])
	runmax = forms.IntegerField(label = '\"Parallel\" runs', validators = [is_positive_integer])
	infile = forms.Field()
	
	def __init__(self, *args, **kwargs):
		''' 
			Override init to get infile choices from user's uploaded files. 
		'''
		user = kwargs.pop('user', None)
		super(SemsepArgs, self).__init__(*args, **kwargs)
		infile = kwargs.pop('infile', None)
		if user is not None:
			self.file_choices = InputFiles.objects.filter(user = user).order_by('name', 'time')
			self.fields['infile'] = forms.ModelChoiceField(label = "Input file", 
												queryset = self.file_choices,
												empty_label = None)
		elif infile is not None: 
			self.fields['infile'] = forms.FileField(infile)		
		

	
class RHMArgs(forms.Form):
	'''
		Form for rhm algorithm's arguments.
	'''	
	itermaxin  = forms.IntegerField(label = 'Iteration max', validators = [is_positive_integer]) 
	strap = forms.IntegerField(label = 'Strap', validators = [is_positive_integer])
	
	def __init__(self, user = AnonymousUser, infile = None, *args, **kwargs):
		''' 
			Override init to get infile choices from user's uploaded files. 
		'''
		super(RHMArgs, self).__init__()
		if user is not AnonymousUser:
			self.file_choices = InputFiles.objects.filter(user = user).order_by('name', 'time')
		else: 
			self.file_choices = [infile]		
		self.fields['infile'] = forms.ModelChoiceField(label = "Input file", queryset = self.file_choices) 
	
	
