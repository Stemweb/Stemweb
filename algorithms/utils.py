'''
	Some utility functions to help algorithm runs, etc.
'''
import os
import string
import random
import logging

from models import Algorithm
from .settings import ARG_VALUE_FIELD_TYPE_KEYS as field_types
from Stemweb import settings
from Stemweb.files.models import InputFile

from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404

nw_display = os.path.join(settings.SITE_ROOT, 'shell_scripts', 'nw_display')

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


def build_run_folder(user, input_file_id, algorithm_name):  
	''' Builds unique path for run's result folder.

		runfile:	 Absolute path to file to use as input_file for a run.
		run_id:		 ID of the R_runs db-table's entry

		Returns path to run's storage folder. All runs' storage folders have 
		structure: 'users', user.username, 'runs', algorithm_name, input_file_id,
		id_generator(). Algorithm name is slugified in the process. 
	'''
	uppath = os.path.join('users')
	uppath = os.path.join(uppath, user.username)
	uppath = os.path.join(uppath, 'runs')
	uppath = os.path.join(uppath, slugify(algorithm_name))
	uppath = os.path.join(uppath, '%s' % input_file_id)
	uppath = os.path.join(uppath, id_generator())
	return uppath


def build_args(form = None, algorithm_id = None, request = None):
	''' Generate running args from given DynamicArgs-form.
		
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
	
	''' Build run folder based on input file's id and algorithm's name. '''		
	run_folder = build_run_folder(request.user, run_args['file_id'], \
		Algorithm.objects.get(pk = algorithm_id).name)
	abs_folder = os.path.join(settings.MEDIA_ROOT, run_folder) 
	os.makedirs(abs_folder)
	run_args['url_base'] = run_folder	# TODO: Hack, fix this
	run_args['outfolder']  = abs_folder
	return run_args


def register(algorithm = None, name = None):
	if type(algorithm) is not Algorithm:
		raise TypeError('Algorithms cannot register type: %s' % type(algorithm))
	
	if name is None and algorithm.name is None:
		name = algorithm.__class__

			