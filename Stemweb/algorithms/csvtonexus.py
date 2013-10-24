#!/usr/bin/python
import sys
import string

chars = list(string.ascii_letters) + list(string.digits) + [x for x in string.punctuation if x is not '?']

def csv2nex(csv_file):
	''' Convert given csv file to nexus format. 
	
		Parameters:
	
		csv_file	: Absolute filepath to the CSV formatted file with tabs as 
					  separators. The CSV file must be already aligned with '-'
					  characters for missing data
				  
		Returns nexus format of the file as a list of lists, where first index 
		of the list constains the name of the taxa and the rest of the list 
		contains taxa.
	'''
	
	with open(csv_file, 'r') as f:
		taxas = [[name.strip() for name in f.readline().split('\t') ]]
		print taxas
		for line in f:
			word_list = [ x.strip() for x in line[:-1].split('\t') ]
			word_set = list(set(word_list) | set([""]))
			word_set.sort()
			result = []
			for w in word_list:
				if w and w != "-":
					result.append(chars[word_set.index(w) - 1])
				else:
					result.append("?")
				taxas.append(result)
				
		for c in taxas:
			print c[0] + "\t" + zip(c[1:]) + "\n"
