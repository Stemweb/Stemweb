'''
	Algorithm forms validators.
'''
from django import forms

def is_positive_integer(IntegerField):
	if IntegerField <= 0:
		raise forms.ValidationError("Value should be positive integer.")
	

