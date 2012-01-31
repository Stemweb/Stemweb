#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_str

#
class Input_files(models.Model):
      
    #user = models.ForeignKey(User)                  # User who uploaded the file
    time = models.DateTimeField(auto_now = True)    # Uploading time 
    #file_type = models.CharField(max_length = 10)   # Type of the file.
    name = models.CharField(max_length = 80)        # Base name of the input file
    path = models.CharField(max_length = 300)       # Absolute file path to this file
    
    def __str__(self):
        return smart_str('%s %s', self.name, self.time)
    
class R_runs(models.Model):
    
    #time = models.DateTimeField(auto_now = True)    # Starting time of the run
    input_file = models.ForeignKey(Input_files)     # Input file of the run
    itermax = models.IntegerField(default = 10)     # Iteration max of the run
    runmax = models.IntegerField(default = 2)       # How many simultaneous runs
    res_folder = models.CharField(max_length = 300) # Absolute path to result folder
    res_pic = models.CharField(max_length = 300)    # Absolute path to resulting .png
    
    def __str__(self):
        return smart_str('%s %s i=%s r=%s', self.input_file.name, self.time, self.itermax, self.runmax)
    
    
    