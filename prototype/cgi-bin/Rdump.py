#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from subprocess import Popen

# Dump "relevant" information of semrunf81.r execution into stdout 
#
# params:
#	web - True if dump is going into webpage
#	runmax - maximum runs of R-file
#	inputfile - input file of the R-script
#	outfolder - folder where R-script puts it's output
def runsemf81(web = False, runmax = 1, inputfile = 'test.nex', outfolder = r'/out/'):

  
  if web:											# This is going into plaintext webpage.
    print "Content-Type: text/plain;charset=utf-8"

  #
  #		Dump all the directories contents with file permissions.
  #

  print 'permissions in %s' % (outfolder)
  p = subprocess.Popen('ls -la', cwd='%s' % (outfolder), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in p.stdout.readlines():
      print line,
  retval = p.wait()

  print
  print 'permissions in %s%s' % (outfolder, inputfile)
  p = subprocess.Popen('ls -la', cwd='%s%s' % (outfolder, inputfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in p.stdout.readlines():
      print line,
  retval = p.wait()

  runs = range(runmax)

  for i in runs:
    print
    print 'permissions in %s%s/run%s' % (outfolder, inputfile, i+1)
    p = subprocess.Popen('ls -la', cwd='%s%s/run%s' % (outfolder, inputfile, i+1), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
	  print line,
    retval = p.wait(),

  #
  # 	Dump R's output in this run. 
  #

  print
  print
  print '%sRout.txt' % (outfolder)

  p = subprocess.Popen(['chmod', '755', '%sRout.txt' % (outfolder)])
  p.wait()

  f = open(r'./../htdocs%sRout.txt' % (outfolder), 'r')
  for line in f:
      print line,
      
  return
    