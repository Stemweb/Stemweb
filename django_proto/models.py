#!/usr/bin/env python
# -*- coding: utf-8 -*-

# All database models (ie. tables). Django creates
# these tables with "python manage.py syncdb" -command.

from django.db import models
#from django.contrib.auth.models import User
from django.utils.encoding import smart_str

# Table for all different script types. Basically determines which
# program needs to be opened for which type of script
class Script_types(models.Model):
    name = models.CharField(max_length = 200)           # Name of the script type. 
    running_program = models.CharField(max_length = 100)# Program to run this script type.
    
    def __str__(self):
        return smart_str('%s %s', self.name, self.running_program)
   
 
# Table for all different scripts.
class Scripts(models.Model):
    time = models.DateTimeField(auto_now = True)    # Time when script was added to database
    script_type = models.ForeignKey(Script_types)   # Type of the script from the Script_types
    name = models.CharField(max_length = 50)        # Name of the script
    path = models.CharField(max_length=200)         # Absolute path to this scripts file.
    
    def __str__(self):
        return smart_str('%s / %s / %s', self.name, self.script_type.name, self.time)

# Basic table for all input files to any of the scripts.   
class Input_files(models.Model):
      
    #user = models.ForeignKey(User)                  # User who uploaded the file
    time = models.DateTimeField(auto_now = True)    # Uploading time 
    #file_type = models.CharField(max_length = 10)   # Type of the file.
    name = models.CharField(max_length = 80)        # Base name of the input file
    path = models.CharField(max_length = 300)       # Absolute file path to this file
    
    def __str__(self):
        return smart_str('%s %s', self.name, self.time)
  
# Basic table to manage different runs of the scripts 
# with different input files.  
class Script_runs(models.Model):
    
    #time = models.DateTimeField(auto_now = True)    # Starting time of the run
    #script = models.ForeignKey(Scripts)             # Script used in this run
    input_file = models.ForeignKey(Input_files)     # Input file of the run
    itermax = models.IntegerField(blank = True)     # Iteration max of the run
    runmax = models.IntegerField(blank = True)      # How many simultaneous runs
    res_folder = models.CharField(max_length = 300) # Absolute path to result folder
    res_pic = models.CharField(max_length = 300)    # name of the resulting .png
    
    def __str__(self):
        return smart_str('%s %s i=%s r=%s', self.input_file.name, self.time, self.itermax, self.runmax)

   

    

    
    
    
    

 

    