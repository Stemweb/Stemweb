#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from recaptcha_works.fields import RecaptchaField
import os

########                                ########
########           VALIDATORS           ########
########                                ########

# Simple validator that check's that FileField's basename 
# is no more than 30 characters long.
def validate_upload_file(FileField):
    filename = os.path.basename(FileField.name)
    if len(filename) > 30:
        raise forms.ValidationError('File\'s name %s is too long. Only 30 characters allowed.' % (FileField.name))

########                                ########
########            THE FORMS           ########
########                                ########

# Simple form to select a file from local system.
class Upload_file(forms.Form):
    upfile = forms.FileField(label='', 
                             max_length=30, 
                             widget=forms.ClearableFileInput(attrs={'size': 30, 'class': 'file_input'}))
    
    captcha = RecaptchaField(label='', required=True)

# Form to choose runsemf81 run's parameters.    
class Run_file(forms.Form):
    iter_choices = ((5, '5'), (10, '10'), (15, '15'), (20, '20'), (25, '25'))
    run_choices = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'))
    
    itermaxin = forms.ChoiceField(label="Iterations", 
                                  choices=iter_choices, 
                                  initial = 15)
    
    runmax = forms.ChoiceField(label="Runs",
                               choices=run_choices, 
                               initial = 2)
    