'''
Created on Jul 6, 2012

@author: slinkola
'''
import os
import re
import logging
from datetime import datetime

import django.forms
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
#from django.template.defaultfilters import slugify

from . import utils
from . import settings
from . import views
from . import models
from . import forms
from . import tasks

from Stemweb import files
import Stemweb

logging.disable(logging.CRITICAL)

class UtilsTestCase(TestCase):
		
	def testBuildRunFolder(self):
		user = User.objects.create(username="test_user", id = 1)
		file_id = 1 
		algo_name = 'test algorithm'
		test_folder = utils.build_run_folder(user, file_id, algo_name)
		compare_folder = os.path.join('users', 'test_user', 'runs', 'test-algorithm', '1')
		common_prefix = os.path.commonprefix([test_folder, compare_folder])
		test_id = os.path.basename(test_folder)
		test_re = re.compile(r"\w{8}")
		self.assertEquals(compare_folder, common_prefix, \
			"build_run_folder does not create proper prefix (without generated id)")
		self.assertTrue(len(test_id) > 0, \
			"last folder of the path has zero length")
		self.assertIsNotNone(test_re.match(test_id), \
			r"Warning: Last folder of the path did not match regular expression '\w{8}'")
		test_re = re.compile(r"\w{9}")
		self.assertIsNone(test_re.match(test_id), \
			r'''Warning: Last folder of the path matched to regular expression '\w{9}'. 
			There should be only 8 characters. While this is not crucial per se 
			(all the folders are stored into database as they are created), it does 
			break the integrity of folder structures. ''')
		
		
class ViewsTestCase(TestCase):
	fixtures = ['algorithms_test_data', 'files_test_data']

	def setUp(self):
		#Stemweb.settings.BROKER_BACKEND = 'memory'
		
		# username: test_user / pwd: test_password
		self.test_user = User.objects.get(id__exact = 1)
		# username: test_user2 / pwd: test_password2
		self.test_user2 = User.objects.get(id__exact = 2)
		self.test_algo = models.Algorithm.objects.get(id__exact = 1)
		self.test_algo2 = models.Algorithm.objects.get(id__exact = 2)
		self.test_file = files.models.InputFile.objects.get(id__exact = 1)
		self.test_file2 = files.models.InputFile.objects.get(id__exact = 2)
		
		test_run = models.AlgorithmRun.objects.create(user = self.test_user, \
			pk = 1, end_time = datetime.now(), algorithm = self.test_algo, \
			input_file = self.test_file, folder = os.path.join(__file__, 'test'))
		test_run.save()
		test_run = models.AlgorithmRun.objects.create(user = self.test_user,\
			pk = 3, end_time = datetime.now(), algorithm =  self.test_algo2, \
			input_file = self.test_file, folder = os.path.join(__file__, 'test3'))
		test_run.save()
		test_run = models.AlgorithmRun.objects.create(user = self.test_user2, \
			pk = 2, end_time = datetime.now(), algorithm = self.test_algo, \
			input_file = self.test_file2, folder = os.path.join(__file__, 'test2'))
		test_run.save()
		self.rqf = RequestFactory()
	
	def testBase(self):
		resp = self.client.get(reverse('algorithms_base_url'))
		self.assertEquals(resp.status_code, 200)
		self.assertTrue('algorithms_base.html' \
			in [t.name for t in resp.templates])
		self.assertTrue('all_algorithms' in resp.context)
		self.assertEquals([algo.pk for algo \
			in resp.context['all_algorithms']], [2,1])
		
	def testDetails(self):
		# Unauthenticated user
		resp = self.client.get(reverse('algorithms_details_url', \
			args=[self.test_algo.pk]))
		self.assertEquals(resp.status_code, 200)
		self.assertTrue('all_algorithms' in resp.context)
		self.assertTrue('algorithms_details.html' \
			in [t.name for t in resp.templates])
		self.assertEquals([algo.pk for algo \
			in resp.context['all_algorithms']], [2,1])
		self.assertIsNone(resp.context['algorithm_runs'], \
			'Algorithm runs is not None when user is not logged in.')
		self.assertIsNotNone(resp.context['form'], \
			'Form for algorithms arguments is none.')
		
		resp = self.client.get(reverse('algorithms_details_url', args=[999999]))
		self.assertEqual(resp.status_code, 404)
		
		# Authenticated user
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.get(reverse('algorithms_details_url', \
			args=[self.test_algo.pk]))
		self.assertEquals(resp.status_code, 200)
		self.assertTrue('algorithms_details.html' \
			in [t.name for t in resp.templates])
		self.assertTrue('all_algorithms' in resp.context)
		self.assertEquals([algo.pk for algo \
			in resp.context['all_algorithms']], [2,1])
		
		# Previous runs for auth user
		algo_runs = resp.context['algorithm_runs']
		self.assertIsNotNone(algo_runs, \
			'Algorithm runs is None when user is logged in and has previous runs.')
		# Only logged user's runs for this particular algorithm should be shown.
		self.assertEquals([run.pk for run in algo_runs], [1], \
			r"algorithm_runs contains other user's and/or other algorithms' runs than current viewed algorithm.") 
		test_run = algo_runs[0]
		self.assertEquals(test_run.algorithm, \
			models.Algorithm.objects.get(id__exact = 1), \
			'Algorithms detail view does not show correct algorithm in previous runs.')
		self.assertEquals(test_run.input_file, \
			files.models.InputFile.objects.get(id__exact = 1), \
			'Algorithms detail view does not show correct input file for previous run.')
		self.assertEquals(test_run.folder, os.path.join(__file__, 'test'), \
			r"Algorithms detail view does not have correct path for previous runs' input files.")
		
	def testDeleteRunsUnauth(self):
		''' Unauthenticated user is redirected to login page. (Redirect should 
		lose all POST data.) '''
		del_url = reverse('algorithms_delete_runs_url')
		login_url = reverse('auth_login')
		redirect_url = "http://testserver" + login_url +"?next=" + del_url
		resp = self.client.get(del_url)
		self.assertEquals(resp.status_code, 302)
		self.assertEquals(resp['Location'], redirect_url)
		
	def testDeleteRunsBadPk(self):
		''' User cannot delete other users' runs. If even one run pk in post is 
		owned by other user, the 400 is returned as response and no runs are 
		deleted. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_delete_runs_url'), \
			{'runs': u"1 2"})
		self.assertEquals(resp.status_code, 400)
		self.assertIsNotNone(models.AlgorithmRun.objects.get_or_none(pk = 1))
		self.assertIsNotNone(models.AlgorithmRun.objects.get_or_none(pk = 2))
		
	def testDeleteRunsNonexistantPk(self):
		''' If there are non-existant run ids, the server does not care and only
		deletes runs that exist in database. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_delete_runs_url'), \
			{'runs': u"1 99999"})
		self.assertEquals(resp.status_code, 200)
		self.assertIsNone(models.AlgorithmRun.objects.get_or_none(pk = 1))
		#self.assertIsNotNone(models.AlgorithmRun.objects.get_or_none(pk = 2))
		
	def testDeleteRunsNormal(self):
		'''User can delete all the runs he/she owns. Even though they are not
		from same algorithm. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_delete_runs_url'), \
			{'runs': u"1 3"})
		self.assertEquals(resp.status_code, 200)
		self.assertIsNone(models.AlgorithmRun.objects.get_or_none(pk = 1))
		self.assertIsNone(models.AlgorithmRun.objects.get_or_none(pk = 3))
		
	def testRunUnAuth(self):	
		''' Unauthenticated user is redirected to login page. '''
		run_url = reverse('algorithms_run_algorithm_url', \
			kwargs = { 'algo_id': 1})
		login_url = reverse('auth_login')
		redirect_url = "http://testserver" + login_url +"?next=" + run_url
		resp = self.client.post(run_url)
		self.assertEquals(resp.status_code, 302)
		self.assertEquals(resp['Location'], redirect_url)
		
	def testRunNonexistantPk(self):
		''' Non-existant Algorithm pk throws 404. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_run_algorithm_url', \
			kwargs = {'algo_id' : 99999}))
		self.assertEquals(resp.status_code, 404)
		
	def testRunNoForm(self):
		''' Authenticated user without POST data should get redirected to 
		algorithm details page. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_run_algorithm_url', \
			kwargs = {'algo_id' : 1}))
		self.assertEquals(resp.status_code, 302)
		redir_url = "http://testserver" + reverse('algorithms_details_url', \
			args = { 1 })
		self.assertEquals(resp['Location'], redir_url, \
			"User was not redirected to details page.")

	def testRunBadForm(self):
		''' Authenticated user with bad form data should get redirected to 
		algorithm details page. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_run_algorithm_url', \
			kwargs = {'algo_id' : 1}), {'foo': 'bar'})
		self.assertEquals(resp.status_code, 302)
		redir_url = "http://testserver" + reverse('algorithms_details_url', \
			args = { 1 })
		self.assertEquals(resp['Location'], redir_url, \
			"User was not redirected to details page.")
		
	def testRunBadInputFile(self):
		''' Trying to give input file that is not in database should redirect
		to algorithm details page. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.post(reverse('algorithms_run_algorithm_url', \
			kwargs = {'algo_id' : 1}), {'itermaxin': 100, 'infile' : 400})
		self.assertEquals(resp.status_code, 302)
		redir_url = "http://testserver" + reverse('algorithms_details_url', \
			args = { 1 })
		self.assertEquals(resp['Location'], redir_url, \
			"User was not redirected to details page.")
	
	def testRunNoPost(self):
		''' Authenticated user with GET-method should throw 404. '''
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.get(reverse('algorithms_run_algorithm_url', \
			kwargs = {'algo_id' : 1}))
		self.assertEquals(resp.status_code, 404)
		self.assertTrue('404.html' in [t.name for t in resp.templates])
		
	def testResults(self):
		test_run = models.AlgorithmRun.objects.get(pk = 1)
		test_run2 = models.AlgorithmRun.objects.get(pk = 2)
		
		# Sanity check
		self.assertEquals(test_run.user, self.test_user, \
			'Something must have changed in loaded test data.')
		self.assertEquals(test_run2.user, self.test_user2, \
			'Something must have changed in loaded test data.')
		self.assertEquals(test_run.algorithm, self.test_algo, \
			'Something must have changed in loaded test data.')
			
		# Unauthenticated user is redirected to login page
		results_url = reverse('algorithms_run_results_url', args=[test_run.pk])
		login_url = reverse('auth_login')
		redirect_url = "http://testserver" + login_url +"?next=" + results_url
		resp = self.client.get(results_url)
		self.assertEquals(resp.status_code, 302)
		self.assertEquals(resp['Location'], redirect_url)
		
		# Authenticated user can see runs made by him/herself and has a valid
		# AlgorithmRun instance in response
		self.client.login(username="test_user", password = "test_password")
		resp = self.client.get(results_url)
		self.assertEquals(resp.status_code, 200)
		self.assertTrue('algorithm_running_results.html' \
			in [t.name for t in resp.templates])
		self.assertTrue('algorithm_run' in resp.context, \
			"No algorithm run defined in http response.")
		algo_run = resp.context['algorithm_run']
		self.assertTrue(type(algo_run) is models.AlgorithmRun, \
			"algorithm_run in context is not of type AlgorithmRun model.")
		
		# Authenticated user can only view runs made by him/herself.
		results_url2 = reverse('algorithms_run_results_url', args=[test_run2.pk])
		resp = self.client.get(results_url2)
		self.assertEquals(resp.status_code, 404)
		
		# Unexistant AlgorithmRun pk should give 404
		results_url2 = reverse('algorithms_run_results_url', args=[999999])
		resp = self.client.get(results_url2)
		self.assertEquals(resp.status_code, 404)

class SettingsTestCase(TestCase):
	fixtures = ['bootstrap.json']
	
	def testArguments(self):
		''' Verify that all ARG_VALUE_CHOICES have entries in field type keys and
		validators. '''
		type_keys = settings.ARG_VALUE_FIELD_TYPE_KEYS
		validators = settings.ARG_VALUE_FIELD_TYPE_VALIDATORS
		for t in settings.ARG_VALUE_CHOICES:
			self.assertTrue(t[0] in type_keys, \
				"Key %s does not have entry in ARG_VALUE_FIELD_TYPE_KEYS, but is in ARG_VALUE_CHOICES" % t[0])
			self.assertTrue(type(type_keys[t[0]]) is type(django.forms.Field), \
				"Type keys: Entry for key %s is not subclass of django.forms.Field" % t[0])
			self.assertTrue(t[0] in validators, \
				"Key %s does not have entry in ARG_VALUE_FIELD_TYPE_VALIDATORS, but is in ARG_VALUE_CHOICES" % t[0])
			self.assertTrue(type(validators[t[0]]) is type(list()), \
				"Validators: Entry for key %s is not a list" % t[0])
	
	def testCallingDictEntries(self):
		''' Verify that all calling dict keys have Algorithm-model with that pk
		and vice versa. '''
		algorithms = models.Algorithm.objects.all()
		algodb_pks = [algo.pk for algo in algorithms]
		call_dict_pks = [int(key) for key in settings.ALGORITHMS_CALLING_DICT.keys()]
		for pk in call_dict_pks:
			self.assertTrue(pk in algodb_pks , \
				"pk=%s found from calling dict but not in database for Algorithm-model." % pk)
			
		for pk in algodb_pks:
			self.assertTrue(pk in call_dict_pks, \
				"pk=%s found from database (Algorithm-model) but not from calling dict." % pk)
			
	def testCallingDictCallables(self):
		''' Verify that all calling dict entries have 'callable' keyword present 
		and that entry for each of these is subclass of AlgorithmTask. '''
		call_dict = settings.ALGORITHMS_CALLING_DICT
		for key in call_dict:
			entry = call_dict[key]
			self.assertIsNotNone(entry['callable'], \
				"Key pk=%s does not have entry for \'callable\'." % (key))
			self.assertTrue(type(entry['callable']) is type(tasks.AlgorithmTask), \
				'%s is not subclass of AlgorithmTask' % type(entry['callable']))
	

class DynamicArgsTestCase(TestCase):
	# TODO: Add testcases with post data. Ensure that error messages are shown.
	fixtures = ['algorithms_test_data', 'files_test_data']

	def setUp(self):
		# username: test_user / pwd: test_password
		self.test_user = User.objects.get(id__exact = 1)
		# username: test_user2 / pwd: test_password2
		self.test_user2 = User.objects.get(id__exact = 2)
		self.test_algo = models.Algorithm.objects.get(id__exact = 1)
		self.test_algo2 = models.Algorithm.objects.get(id__exact = 2)
		self.test_file = files.models.InputFile.objects.get(id__exact = 1)
		self.test_file2 = files.models.InputFile.objects.get(id__exact = 2)
		
		test_run = models.AlgorithmRun.objects.create(user = self.test_user,
													pk = 1,
													end_time = datetime.now(),
													algorithm = self.test_algo,
													input_file = self.test_file,
													folder = os.path.join(__file__, 'test'))
		test_run.save()
		test_run3 = models.AlgorithmRun.objects.create(user = self.test_user,
													pk = 3,
													end_time = datetime.now(),
													algorithm =  self.test_algo2,
													input_file = self.test_file,
													folder = os.path.join(__file__, 'test3'))
		test_run3.save()
		test_run2 = models.AlgorithmRun.objects.create(user = self.test_user2,
													pk = 2,
													end_time = datetime.now(),
													algorithm = self.test_algo,
													input_file = self.test_file2,
													folder = os.path.join(__file__, 'test2'))
		test_run2.save()

	def testInitLoggedOut(self):
		''' Verify that dynamic arguments are created correctly for non-authenticated users. '''
		
		form = forms.DynamicArgs(arguments = self.test_algo.args, post = None)
		qlen = len(form.fields['infile'].queryset)
		self.assertFalse(qlen > 0, "Input file has entries in queryset for unauthenticated user.")
		self.assertTrue(len(form.fields) is 2, \
			"Not right amount of form fields (expected 1, got %s)." % len(form.fields))

	def testInitLoggedIn(self):
		''' Verify that dynamic arguments are created correctly for authenticated users. '''
		
		self.client.login(username="test_user", password = "test_password")
		form = forms.DynamicArgs(arguments = self.test_algo.args, 
								user = self.test_user, post = None)
		len_if = len(form.fields['infile'].queryset)
		self.assertTrue(len_if is 2, \
			"Not right amount of input files (expected 2, got %s)." % len_if)
		self.assertTrue(len(form.fields) is 2, \
			"Not right amount of arguments (expected 2, got %s)." % len(form.fields))
		arguments = self.test_algo.args.all()
		for f in form.fields:
			self.assertTrue(f in [arg.key for arg in arguments], \
				"Form-fields key \'%s\' not a key for any of the %s\'s arguments found in database." \
				% (f, self.test_algo.name))
		
		for f in form.fields['infile'].queryset:
			self.assertTrue(f.user.pk is self.test_user.pk, \
				r"DynamicArgs shows other users' files as possible input files for logged in user.")
			
		
		
		
		
'''	
	some test cases:
		User cannot run algorithm with another users file
			- directly by putting it as an parameter to algorithm
			- another users files don't show in dynamic arg form 
		
		User cannot "hack" their way to another users files / algorithm results via spesific urls
			- this probably needs some tweaking from apache side?
		

		
class AlgorithmTaskTestCase(TestCase):

	def setUp(self):
	
	def testBase(self):
	
	def testNJ(self):
		
	def testNN(self):
		
	def testSemstem(self):

	def testRHM(self):

'''
		


		
		

		
		
		
		
		
		
		