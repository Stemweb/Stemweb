#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms

# Simple form to select a file from local system.
class Upload_file(forms.Form):
    upfile = forms.FileField()
