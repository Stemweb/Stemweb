#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
import utils

# Basic table for all input files for different scripts that user has created.   
class Input_files(models.Model):
      
    # User who uploaded the file
    user = models.ForeignKey(User)        
    
    # Uploading time. Shouldn't be changed, unless you allow user to edit
    # their uploaded files afterwards, but that is risky and all the editing
    # should be verified afterwards before allowing user to run the file.          
    time = models.DateTimeField(auto_now_add = True)  
    
    # File extension. Kinda irrelevant, because it can be splitted from name.
    file_ext = models.CharField(max_length = 10, default = 'nex')   
    
    # Base name of the input file
    name = models.CharField(max_length = 80)        
    
    # FileField for the file for convenience functions like .url and .open
    # This FileField is automatically created when the object is created.
    file_field = models.FileField(upload_to = utils.upload_path)       
    
    # Absolute file path to this file. This is created when file_field
    # call utils.upload_path. So there _might_ be some inconsisties if
    # this can be left blank if file_field object is created before this.
    path = models.CharField(max_length = 200, blank = True, default = file_field.get_directory_name())  
    
    def __str__(self):
        return smart_str('%s %s' % (self.name, self.time))