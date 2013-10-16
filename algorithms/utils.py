'''
	Some utility functions to help algorithm runs, etc.
'''
import os
import string
import random
import logging

from models import Algorithm
from .settings import ARG_VALUE_FIELD_TYPE_KEYS as field_types
from .settings import TRUSTED_SERVERS
from Stemweb import settings
from Stemweb.files.models import InputFile

from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404

nw_display = os.path.join(settings.NEWICK_UTILS, 'nw_display')

def newick2svg(newick, filepath, branch_length = True, radial = True, width = 800):
	'''
		Create svg file from given newick file.
		
		newick			absolute path to newick tree file
		
		filepath		absolute path to svg file to be created
		
		branch_length	boolean, if true shows branch lengths in numeric form
		
		radial			boolean, if true draws radial graph instead of "normal".
		
		width			width of the resulting svg file in pixels. 
	'''
	#nw_display = os.path.join(settings.SITE_ROOT, 'shell_scripts', 'nw_display')
	bl = ' -b \'visibility:hidden\' ' if branch_length is False else ''
	r = ' -r ' if radial is True else ''	
	opt_arg = "%s %s" % (r, bl)
	cmd = "%s -s -R 50 -S %s -w %s %s > %s" % (nw_display, opt_arg, width, newick, filepath)
	os.system(cmd)
	
	
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
	''' Semiunique ID generator -- copypaste code.

		Source:	http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits

		size:	length of the random string. Default 8.
		chars:	set of chars from which the string is created

		Returns random string.
	'''
	return ''.join(random.choice(chars) for x in range(size))


def __build_run_folder__(user, input_file_id, algorithm_name):  
	''' Builds unique path for algorithm run's result folder. Does not create 
		the folder.

		runfile:	 Absolute path to file to use as input_file for a run.
		run_id:		 ID of the R_runs db-table's entry

		Returns path to run's storage folder. All runs' storage folders have 
		structure: 'users', user.username, 'runs', algorithm_name, input_file_id,
		id_generator(). Algorithm name is slugified in the process. 
		
	'''
	if not user.is_authenticated():
		uppath = os.path.join('external')
	else:
		uppath = os.path.join('users')
		uppath = os.path.join(uppath, user.username)
	uppath = os.path.join(uppath, 'runs')
	uppath = os.path.join(uppath, slugify(algorithm_name))
	uppath = os.path.join(uppath, '%s' % input_file_id)
	uppath = os.path.join(uppath, id_generator())
	return uppath


def create_run_folder(user, input_file_id, algorithm_name):
	''' Create unique folder for algorithm run's results. 
	
	Returns folder url for the run, join this path with MEDIA_ROOT to get
	absolute path of the folder.
	'''
	folder_url = __build_run_folder__(user, input_file_id, \
										algorithm_name)
	abs_folder = os.path.join(settings.MEDIA_ROOT, folder_url) 
	try:
		os.makedirs(abs_folder)
	except:
		logger = logging.getLogger("stemweb.algorithm_run")
		logger.error("Could not create algorithm run folder %s" % abs_folder)
	
	return folder_url


def build_local_args(form = None, algorithm_id = None, request = None):
	''' Generate arguments from given DynamicArgs-form for an algorithm run and
		creates preferred directories for output files.
		
		Returns dictionary with running arguments. 
	'''
	run_args = {}
	for key in form.cleaned_data.keys():
		if type(form.fields[key]) == field_types['input_file']:
			input_file = form.cleaned_data[key]
			run_args[key] = input_file.file.path
			run_args['%s_id' % (key)] = input_file.id
			run_args['file_id'] = input_file.id	# TODO: Hack, use upper line.
			input_file.save() # Save it to change last_access
		else:
			run_args[key] = form.cleaned_data[key]
	
	''' Create run folder based on input file's id and algorithm's name. '''		
	run_args['folder_url'] = create_run_folder(request.user, run_args['file_id'], \
		Algorithm.objects.get(pk = algorithm_id).name)	
	return run_args


def build_external_args(algo_id = None, json_data = None, input_file = None):
	
	
	
	pass


def register(algorithm = None, name = None):
	if type(algorithm) is not Algorithm:
		raise TypeError('Algorithms cannot register type: %s' % type(algorithm))
	
	if name is None and algorithm.name is None:
		name = algorithm.__class__
		
		
def validate_server(request):
	''' Validate, that request is send from trusted server. 
	
		Returns true if it is, otherwise false.
	''' 
	
	addr = request.META['REMOTE_ADDR']
	port = request.META['SERVER_PORT']
	trusted_server = False
	
	for server in TRUSTED_SERVERS:
		if server['addr'] == addr:
			trusted_server = True
	
	if trusted_server:
		return (True, None)
	else:
		return (False, "%s:%s not in trusted server list" % (addr, port))
	
	
def validate_json(json_data, algo_id):
	''' Validate that json contains all the needed parameters for external 
	algorithm run.
	
	returns 2-tuple (boolean, error message). If boolean is true, json
	is valid, otherwise error message should send some light into why the query
	failed.
	'''
	algorithm = Algorithm.objects.get_or_none(pk = algo_id)
	if algorithm is None: return (False, "No such algorithm id.")
	
	userid = json_data.pop('userid', None)
	if userid is None: return (False, "No userid given.")
	
	params = json_data['parameters']
	
	args_present = True
	for arg in algorithm.args.all():
		if arg.send_to_external:
			if params.has_key(arg.key):
				value = params[arg.key]
				if not validate_parameter(value, arg.value):
					return (False, "Parameter %s = %s had wrong type. Expected %s." %\
						(arg.key, value, arg.value))
			else: 
				return (False, "No parameter %s present" % (arg.key))
			
	return (True, "")
				
		
def validate_parameter(value, param_type):
	''' Validate, that value can be converted safely into param_type. '''
	if param_type == "positive_integer":
		if type(int(value)) == int:
			return int(value) > 0
		else: 
			return False
	if param_type == "integer":
		return type(int(value)) == int
	if param_type == "float":
		return type(float(value)) == float
	if param_type == "boolean":
		if value.lower() == ("false" or "true"):
			return True
		else:
			return False
	if param_type == "string":
		return type(str(value)) == str
	return False
	
		
					
	
	

			