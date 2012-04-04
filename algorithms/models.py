from django.db import models
from django.utils.encoding import smart_str
from Stemweb.django_proto import handler
from Stemweb.django_proto.models import InputFiles
from django.contrib.auth.models import User

# Table for all different algorithm types. Basically determines which
# program needs to be opened for which type of script
class AlgorithmTypes(models.Model):
	name = models.CharField(max_length = 200)           # Name of the script type. 
	running_program = models.CharField(max_length = 100)# Program to run this script type.

	def __str__(self):
		return smart_str('%s %s' % (self.name, self.running_program))
	
	
# Table for all different algorithms.
class Algorithm(models.Model):
	'''
		Base information of all the different algorithms. 
		Attributes which are passed to certain algorithm are found from
		Attributes-table with algorithm's id.
	'''
	
	#algorithm_type = models.ForeignKey(Algorithm_types)   # Type of the script from the Script_types
	desc = models.CharField(max_length = 2000, blank = True)	
	url = models.URLField(blank = True)
	name = models.CharField(max_length = 50)        # Name of the algorithm
	source = models.CharField(max_length = 200)

	def __str__(self):
		return smart_str('%s / %s / %s' % (self.name, self.algorithm_type.name, self.time))


# Basic table to manage different runs of the scripts 
# with different input files.  
class AlgorithmRuns(models.Model):

	time = models.DateTimeField(auto_now_add = True, null = True) # Starting time of the run
	algorithm = models.ForeignKey(Algorithm)             # Script used in this run
	input_file = models.ForeignKey(InputFiles)     # Input file of the run
	itermax = models.IntegerField(blank = True)     # Iteration max of the run
	runmax = models.IntegerField(blank = True)      # How many simultaneous runs
	folder = models.CharField(max_length = 200, blank = True) # Absolute path to result folder  
	user = models.ForeignKey(User)
	
	image = models.ImageField(upload_to = handler.image_path)    

	def __str__(self):
		return smart_str('%s %s' % (self.input_file.name, self.time))


class Attributes(models.Model):
	'''
		All attributes for algorithms. Creator of the instance must make sure
		that all the fields have correct information which can be safely passed
		to algorithm by creating run_args dictionary from key-value pairs 
		where algorithm's id matches to foreign key.
	'''
	# Algorithm to which this attribute belongs.
	algorithm = models.ForeignKey(Algorithm)
	# Short human readable name of the attribute.
	name = models.CharField(max_length = 30)
	# Long description of the attribute.
	desc = models.CharField(max_length = 3000, default = "No description.")
	# Key of the attribute as used in algorithm's run_args.
	key = models.CharField(max_length = 30)
	# Accepted values for this attribute key. When creating instance change
	# this to ie. PositiveIntegerField, DecimalField or CharField
	accepted_values = models.Field()
	
	