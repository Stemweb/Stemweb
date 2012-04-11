import os
import shutil
import logging

from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django import forms

from Stemweb.files.models import InputFile
from .settings import ARG_VALUE_CHOICES, ARG_VALUE_FIELD_TYPE_KEYS, ARG_VALUE_FIELD_TYPE_VALIDATORS
from .settings import ALGORITHMS_CALLING_DICT as call_dict

	
class AlgorithmArg(models.Model):
	'''
		All algorithms running arguments. 
		
		These are stored as key-value strings in database and form is build by
		corresponding algorithms' build_form() method.
		
		key		Keyword for using this argument as parameter in algorithm.
		
		value	Type of the value used when building this arguments form field. 
				Used to generate right type of form field and pass right kind of 
				validators to field. For accepted values see ''.
				
				TODO: write that see
				
		verbose_name	Human readable name of the argument presented in browser.
		
		description		Optional, longer description of this argument.
	'''
	value_choices = ARG_VALUE_CHOICES
	
	key = models.CharField(max_length = 50)
	value = models.CharField(max_length = 50, choices = value_choices)
	verbose_name = models.CharField(max_length = 100)
	description = models.CharField(max_length = 2000, blank = True)
	
	class Meta:
		ordering = ['key', 'value']
		
	
class Algorithm(models.Model):
	'''
		Base model for all algorithms. Contains information like name,
		page url, name, source of the code and running arguments. 
		Add your algorithms here and remember to link the callable algorithm
		instance into this model. Most likely that will be instance of 
		stoppable_algorithm subclass.  
		
		desc:	Short description of algorithm. Max length 2000.
		
		template:	Algorithm's long descripion template's name. Must be found
					from Stemweb.settings.TEMPLATE_DIRS.
		
		paper:	URL to algorithm's original paper, if available.
		
		url:	Url to this algorithm's webpage. Can be useful when listing all 
				algorithms somewhere. 
				
		name:	Human readable name of the algorithm. Max length 50.
		
		source:	Absolute path to source code of the algorithm. Might be useful 
				if we want to allow users to see the source in the future.
				Max length 200.
				
		args:	Keyword arguments given to this algorithm. You can build form 
				consisting of these arguments by calling build_form. 
				
		stoppable:	Are this algorithm's instances subclasses of 
					StoppableAlgorithm.
			
	'''
	desc = models.CharField(max_length = 2000, blank = True)
	template = models.CharField(max_length = 100, blank = True)	
	paper = models.URLField(blank = True)
	url = models.URLField(blank = True)
	name = models.CharField(max_length = 50)
	source = models.CharField(max_length = 200)
	stoppable = models.BooleanField(default = False)
	args = models.ManyToManyField(AlgorithmArg, blank = True)

	def __str__(self):
		return '''
					name:		%s
					desc:		%s
					url:		%s
					source:		%s
					args:		%s
					stoppable:	%s	
				''' % (self.name, self.desc, self.template, self.source, self.args, self.stoppable)
				
	
	def get_callable(self, kwargs):
		'''
			Update run_args dictionary with all the keys from settings 
			ALGORITHM_CALLING_DICT except 'callable' itself which is returned.
			
			Any keys that are present in run_args already are not updated.
		'''
		algo_callable = None		
		for key, value in call_dict[str(self.id)].items():
			if key == 'callable':
				algo_callable = value
			elif key not in kwargs['run_args']:
				kwargs['run_args'][key] = value
				
		return algo_callable
	

	def build_form(self, user = AnonymousUser, post = None):
		'''
			Build form from args of this algorithm instance. The form is build
			again for each call of this function and is not stored to this model 
			itself. 
			
			Returns subclass of form.Form which has algorithm's keyword 
			arguments as fields. If there are no arguments in args then returns
			None.
			
			user:	User who is currently active in this session. Only this 
					user's files will be shown as possible input files.
			
			post:	request.POST to populate form fields so that is_valid() 
					can be called. Don't use this if you expect user's to 
					populate the fields.
		'''
		if len(self.args.all()) == 0:
			return None
		
		ftypes =  ARG_VALUE_FIELD_TYPE_KEYS
		field_validators = ARG_VALUE_FIELD_TYPE_VALIDATORS
		
		form = forms.Form()
		for arg in self.args.all():
			key, value, name = arg.key, arg.value, arg.verbose_name
			kwargs = {'label': name, 'validators': field_validators[value]}
			if value == 'input_file':
				''' 
					Input File fields are populated dynamically from users 
				 	input files 
				'''
				if user.is_authenticated():
					kwargs['queryset'] = InputFile.objects.filter(user__exact = user)
					form.fields[key] = ftypes[value](**kwargs)			
					'''
						TODO: add AnonymousUser logic here
					'''
			else:			
				form.fields[key] = ftypes[value](**kwargs)
		'''
			If there is request, we change form's fields to correspond request's
			key values.
			
			TODO: do this populating somewhere else.
		'''				
		if post is not None:
			for key in post.keys():
				form.data[key] = post[key]
			form.is_bound = True
		return form
	
	class Meta:
		ordering = ['name']

			
class AlgorithmRun(models.Model):
	'''
		Base information of all the different runs of algorithms.
		
		start_time	: When run was started. Basically the time when this instance
					  was created.
		
		end_time	: When run ended. This can mean either that run was stopped
					  by user or it ended normally (converged or not).
		
		finished	: Is the run finished already. For quick checking.
		
		pid			: Process id of the still running algorithm. When algorithm 
					  stops value is changed to -1.
		
		algorithm	: Algorithm used for this run. Foreign key to Algorithm-
					  model
		
		input_file	: Input file used for this run. Foreign key to InputFile-
					  model.
					  
		folder		: Absolute path to folder where results are. Max length 200.
		
		user		: User who started this run. This cannot be AnonymousUser, 
					  so only store runs which are made by registered users.
					  
		image		: Image of this run's resulting graph of best scored 
					  network structure.
					  
		score		: Score for this run. If algorithm doesn't have score's 
					  this is null. Algorithms which have score must set this 
					  value to other than null when initiating run. Otherwise
					  it can cause rendering issues in browser.
					  
		TODO: change images and folder to be in the results, probably.  
	'''
	start_time = models.DateTimeField(auto_now_add = True)
	end_time = models.DateTimeField(auto_now_add = False, null = True)
	finished = models.NullBooleanField(default = False)
	pid = models.IntegerField(default = -1)
	algorithm = models.ForeignKey(Algorithm)        
	input_file = models.ForeignKey(InputFile)   
	folder = models.CharField(max_length = 200) 
	user = models.ForeignKey(User)
	image = models.ImageField(upload_to = folder, null = True) 
	score = models.FloatField(null = True, verbose_name = "Score")
	current_iteration = models.PositiveIntegerField(null = True)
	#task = models.ForeignKey(djangotasks.Task, null = True)
	
	''' 
		Really we will be wanting to have this as PickleField.
	'''
	#results = dict()
	
	def start(self):
		return 0
		'''
		logger = logging.getLogger('stemweb.algorithm_run')
		logger.info('in start nowwww')
		self.kwargs['algorithm_run'] = self
		ALGORITHM_CALLABLES["%s" % self.algorithm.id](**self.kwargs).run()
		return 0
		'''
	
	def delete(self):
		'''	
			Deletes all the run's results from hard drive so that there are no
			files in users/-subfolders with zero links to them in database.
			
			IMPORTANT: Caller needs to verify that current active user has the
			rights to delete this run. For now it means that self.user is the
			same as request.user.
		'''
		
		# TODO: we need to first check that run has been finished before any
		# deleting can be done.
		try:
			for root, dirs, files in os.walk(self.folder):
				for f in files:
					os.remove(os.path.join(root, f))
				for d in dirs:
					shutil.rmtree(os.path.join(root, d))
			os.rmdir(root)
		except:
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun could not delete files: %s:%s folder:%s' % (self.algorithm.name, self.id, self.folder))
			return -1
			
		models.Model.delete(self)
	
	def __str__(self):
		retval = ''
		for name in self._meta.get_all_field_names():
			retval += "%s: %s \n" % (name, self.__getattribute__(name))
			
		#if self.kwargs:
		#	for k, v in self.kwargs.items():
		#		retval += "%s: %s \n" % (k, v)
		return retval
	
	class Meta:
		ordering = ['finished', '-end_time', '-start_time']
	
	