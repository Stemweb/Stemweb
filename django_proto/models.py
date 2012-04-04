#!/usr/bin/env python
# -*- coding: utf-8 -*-

# All database models (ie. tables). Django creates
# these tables with "python manage.py syncdb" -command.

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
import handler


# Basic table for all input files to any of the scripts.   
class InputFiles(models.Model):
      
    user = models.ForeignKey(User)                  # User who uploaded the file
    time = models.DateTimeField(auto_now_add = True) # Uploading time 
    file_ext = models.CharField(max_length = 10, default = 'nex')   # File extension
    name = models.CharField(max_length = 80)        # Base name of the input file
    file_field = models.FileField(upload_to = handler.upload_path)
    path = models.CharField(max_length = 200, blank = True, default = file_field.get_directory_name())       # Absolute file path to this file
    
    def __str__(self):
        return smart_str('%s %s' % (self.name, self.time))
  
# Basic table to manage different runs of the scripts 
# with different input files.  
class AlgorithmRuns(models.Model):
    
    time = models.DateTimeField(auto_now_add = True, null = True) # Starting time of the run
    #script = models.ForeignKey(Scripts)             # Script used in this run
    input_file = models.ForeignKey(InputFiles)     # Input file of the run
    itermax = models.IntegerField(blank = True)     # Iteration max of the run
    runmax = models.IntegerField(blank = True)      # How many simultaneous runs
    folder = models.CharField(max_length = 200, blank = True) # Absolute path to result folder  
      
    # REFACTOR THIS TO models.ImageField
    image = models.ImageField(upload_to = handler.image_path)    
    
    
    
    def __str__(self):
        return smart_str('%s %s' % (self.input_file.name, self.time))
    
    
    
    

 

    