import os
import shutil
import logging

from django.db import models
from django.contrib.auth.models import User, AnonymousUser

from forms import DynamicArgs
from Stemweb.files.models import InputFile
from .settings import ARG_VALUE_CHOICES, STATUS_CODES
from .settings import ALGORITHMS_CALLING_DICT as call_dict


class GetOrNoneManager(models.Manager):
	"""Adds get_or_none method to objects
    """
	def get_or_none(self, **kwargs):
		try:
			return self.get(**kwargs)
		except self.model.DoesNotExist:
			return None


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
				
		name			Human readable name of the argument presented in browser.
		
		description		Optional, longer description of this argument.
		
		external		Will this argument be sent to external server
	'''
	value_choices = ARG_VALUE_CHOICES
	
	key = models.CharField(max_length = 50)
	value = models.CharField(max_length = 50, choices = value_choices)
	name = models.CharField(max_length = 100)
	description = models.CharField(max_length = 2000, blank = True)
	external = models.BooleanField(default = True)
	
	class Meta:
		ordering = ['value', 'key', 'name']
		
	
class Algorithm(models.Model):
	''' Base model for all algorithms. Contains information like name,
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
					
		newick:	Does this algorithm have newick tree output. 
			
	'''
	desc = models.CharField(max_length = 2000, blank = True)
	template = models.CharField(max_length = 100, blank = True)	
	paper = models.URLField(blank = True)
	url = models.URLField(blank = True)
	name = models.CharField(max_length = 50)
	source = models.CharField(max_length = 200, null = True)
	stoppable = models.BooleanField(default = False)
	args = models.ManyToManyField(AlgorithmArg, blank = True)
	file_extension = models.CharField(max_length = 5, default = 'nex')

	def __str__(self):
		return '''
					name:		%s
					desc:		%s
					url:		%s
					source:		%s
					args:		%s
					stoppable:	%s	
				''' % (self.name, self.desc, self.template, self.source, \
					self.args, self.stoppable)
				
	
	def get_callable(self, kwargs):
		''' Update run_args dictionary with all the keys from settings 
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
	

	def args_form(self, user = AnonymousUser, post = None):
		'''
			Build form from args of this algorithm instance. The form is build
			again for each call of this function and is not stored to this model 
			itself. 
			
			Returns instance of DynamicArgs form which has algorithm's keyword 
			arguments as fields. If there are no arguments in args then returns
			None.
			
			user:	User who is currently active in this session. Only this 
					user's files will be shown as possible input files.
			
			post:	request.POST to populate form fields so that is_valid() 
					can be called. Don't use this if you expect user's to 
					populate the fields.
		'''
		if len(self.args.all()) == 0: return None
		return DynamicArgs(arguments = self.args, user = user, post = post)
	
	
	def get_external_args(self):
		''' Get all algorithms arguments that will be send to external server. 
		'''
		external_args = []
		for arg in self.args.all():
			if arg.external:
				external_args.append(arg)
				
		return external_args
			
			
	class Meta:
		ordering = ['name']
	
	objects = GetOrNoneManager()

			
class AlgorithmRun(models.Model):
	''' Base information of all the different runs of algorithms.
		
		start_time	: When run was started. Basically the time when this instance
					  was created.
		
		end_time	: When run ended. This can mean either that run was stopped
					  by user or it ended normally (converged or not).
		
		finished	: Is the run finished already. For quick checking.
		
		algorithm	: Algorithm used for this run. Foreign key to Algorithm-
					  model
		
		input_file	: Input file used for this run if the run is not external. 
					  Foreign key to InputFile-model.
					  
		folder		: Absolute path to folder where results are, is run is not
					  external. Max length 200.
		
		user		: User who started this run. This cannot be AnonymousUser. 
					  If no user field is blank, external must be True and ip
					  should have valid response ip when this algorithm run 
					  finishes.
					  
		image		: Image of this run's resulting graph of best scored 
					  network structure (if available).
					  
		score		: Score for this run. If algorithm doesn't have score
					  this is null. Algorithms which have score must set this 
					  value to other than null when initiating run. Otherwise
					  it can cause rendering issues in browser.
					  
		newick		: Resulting newick file of the run.
		
		external	: Boolean, True if external server send this run request, 
					  false otherwise.
					  
		ip			: If algorithm run is external, should have valid response
					  ip. Probably the same ip the algorithm run request was
					  made.
					  
		TODO: change images and folder to be in the results, probably.  
	'''
	start_time = models.DateTimeField(auto_now_add = True)
	end_time = models.DateTimeField(auto_now_add = False, null = True)
	status = models.IntegerField(default = STATUS_CODES['not_started'])
	algorithm = models.ForeignKey(Algorithm)        
	input_file = models.ForeignKey(InputFile, blank = True)   
	folder = models.CharField(max_length = 300, blank = True) 
	user = models.ForeignKey(User, blank = True)
	image = models.ImageField(upload_to = folder, null = True) 
	score = models.FloatField(null = True, verbose_name = "Score")
	current_iteration = models.PositiveIntegerField(null = True)
	newick = models.URLField(blank = True, default = '')
	external = models.BooleanField(default = False)
	ip = models.IPAddressField(null = True)
	
	# Really we will be wanting to have this as PickleField.
	#results = dict()
	
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
			# If there is an exception, log it (and probably inform admins about 
			# it), but still delete run for end users convenience.
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun could not delete files: %s:%s folder:%s' \
				% (self.algorithm.name, self.id, self.folder))
			
		models.Model.delete(self)
	
	def __str__(self):
		retval = ''
		for name in self._meta.get_all_field_names():
			retval += "%s: %s \n" % (name, self.__getattribute__(name))
			
		return retval
	
	class Meta:
		ordering = ['status', '-end_time', '-start_time']
	
	objects = GetOrNoneManager()
	
	
	
	
	