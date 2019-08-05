'''
	Some utility functions to help algorithm runs, etc.
'''
import os
import string
import random
import logging

from django.conf import settings
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404

from Bio import Phylo
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from threading import Lock

from models import Algorithm
from .settings import ARG_VALUE_FIELD_TYPE_KEYS as field_types
# from .settings import TRUSTED_SERVERS
from .settings import ALGORITHM_MEDIA_ROOT as algo_media
from Stemweb.files.models import InputFile
from decorators import synchronized

pylab_lock = Lock()

@synchronized(pylab_lock)
def newick2img(newick, filepath, branch_length = True, radial = True, width = 800):
	'''
		Create image file from given newick file. This method has it's own lock so
		that many newick's cannot be drawn into same figure and thus corrupt resulting
		image file.

		newick			absolute path to newick tree file

		filepath		absolute path to svg file to be created

		branch_length	boolean, if true shows branch lengths in numeric form

		radial			boolean, if true draws radial graph instead of "normal".

		width			width of the resulting svg file in pixels.
	'''
	prog = 'dot' if radial else 'neato'
	nwk = Phylo.read(newick, 'newick')
	Phylo.draw_graphviz(nwk, prog = prog, node_size = 500)
	#Phylo.draw(nwk, do_show = False)
	plt.savefig(filepath)


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
	if user is None:
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
	abs_folder = os.path.join(algo_media, folder_url)
	try:
		os.makedirs(abs_folder)
	except:
		logger = logging.getLogger("stemweb.algorithm_run")
		logger.error("Could not create algorithm run folder %s" % abs_folder)

	return folder_url


def build_local_args(form = None, algorithm_name = None, request = None):
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
		algorithm_name)
	return run_args


def build_external_args(parameters, input_file_key, input_file, \
					algorithm_name = None):
	run_args = {}
	for key, value in parameters.items():
		run_args[key] = value
	run_args[input_file_key] = input_file.file.path
	run_args['folder_url'] = create_run_folder(None, input_file.id, algorithm_name)
	return run_args


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
	trusted_server = True

	# for server in TRUSTED_SERVERS:
	# 	m = server['re'].search(addr)
	# 	if m != None and m.start() == 0:
	# 		trusted_server = True

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

	if 'userid' not in json_data: return (False, "No userid given.")
	if 'data' not in json_data: return (False, "No data key present")
	if 'parameters' not in json_data: return (False, "No parameters present")

	params = json_data['parameters']
	for arg in algorithm.args.all().filter(external = True):
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
		if type(value) == int:
			return value > 0
		else:
			return False
	if param_type == "integer":
		return type(value) == int
	if param_type == "float":
		return type(value) == float
	if param_type == "boolean":
		if type(value) == bool:
			return True
		else:
			return False
	if param_type == "string":
		return type(str(value)) == str
	return False
