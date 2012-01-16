#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import sys
import os

# 	Verify that POST-arguments from cgi.FieldStorage are correct
# 	for runsemf81.r
#
#	Changes some arguments like itermaxin and run max to decent
#	values if they are absurd and cancels scripts run if uploaded
# 	file is in wrong format or too big. Default MAX_FILE_SIZE for
# 	uploaded files is 10000.
#
#	params:
#		fs - cgi.FieldStorage instance to verify arguments from.
#
#	Returns checked and possibly corrected arguments as key-value
#	pairs. In case of bad upload file or cgi.FieldStorage is None 
#	returns -1.
#	
def runsemf81(fs = None):
  #if fs is None:
	#print 'No cgi.FieldStorage to verify in verifyFS.py - post(fs)'
	#return -1
	
  run_args = dict()
  
  MAX_FILE_SIZE = 10000
  
  if fs.has_key('MAX_FILE_SIZE'):
	MAX_FILE_SIZE = fs.getfirst('MAX_FILE_SIZE')
  
  if fs['upfile'] is not None:
	extension = os.path.splitext(fs['upfile'].filename)[1]
	if extension != '.nex':
	  print 'File needs to be .nex. Stopping script.'
	  return -1

	#print 'Found file %s' % (fs['upfile'].filename) 
	#uf = fs
	#f = open(uf)
	#print 'ooo'
	#print sys.getsizeof(f)
	#if sys.getsizeof(f) > MAX_FILE_SIZE:
	  #print 'File %s with size %s is too big.' % (fs['upfile'].filename, sys.getsizeof(f))
	  #print 'Maximum file size is %s' % (MAX_FILE_SIZE)
	  #return -1

  if fs.has_key('runmax'):
	runmax = fs.getfirst('runmax')
	if (runmax > 0 and runmax < 10):
	  runmax = 2
	  print 'Changed runmax to %s' % (runmax)
	run_args['runmax'] = runmax
  
  if fs.has_key('itermaxin'):
	itermaxin = fs.getfirst('itermaxin')
	if (itermaxin > 0 and itermaxin < 20):
	  itermaxin = 10 
	  print 'Changed itermaxin to %s' % (itermaxin)
	run_args['itermaxin'] = itermaxin
	
  return run_args