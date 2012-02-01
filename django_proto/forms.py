#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms

# Simple form to select a file from local system.
class Upload_file(forms.Form):
    upfile = forms.FileField()

# Form to choose runsemf81 run's parameters.    
class Run_file(forms.Form):
    iter_choices = ((5, '5'), (10, '10'), (15, '15'), (20, '20'), (25, '25'))
    run_choices = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'))
    itermaxin = forms.ChoiceField(choices=iter_choices, initial = 15)
    runmax = forms.ChoiceField(choices=run_choices, initial = 2)
    