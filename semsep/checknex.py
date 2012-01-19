#!/usr/bin/env python

# the function for checking the right nex file
# isnex = 1 for right format
# -1  --> -8 for wrong format: see comment in the function
# see print message for different errors


def checknex(infile):
	import re

	isnex = 1

	file = open(infile,'r')
	nexin = file.read()
	file.close()
	
	nexin = nexin.strip()
	nexin = nexin.split('\n')
	
	i = 0
	startline = -1
	endline = -1
	for nexinline in nexin:
		nexinline = nexinline.lower()
		if len(re.findall('matrix',nexinline))==1:
			startline = i
		if len(re.findall('end;',nexinline))==1:
			endline = i		
		i = i+1
	
	if (startline < 0):
		isnex = -1
		print ('Wrong nex format! Please define the starting line of the data matrix!')
	elif (endline <0):
		isnex = -2
		print ('Wrong nex format! Please define the end line of the data matrix!')
	elif (endline - startline <= 1):
		isnex = -3
		print ('Wrong nex format! No contents in data matrix!')
	else:
		nodename = []
		nodelen = []
		for i in range(startline+1,endline):
			nexinline = nexin[i]
			nexinline = nexinline.strip()
			if len(nexinline) > 0:
				nexinline = nexinline.split('\t')
				if len(nexinline) != 2:
					isnex = -4
					print ('Wrong nex format! Please separate the document name and contents by Tab!')
					break
				else:
					if len(re.findall(r'[a-zA-Z]',nexinline[0])) == 0:
						isnex = -5
						print ('Wrong nex format! Please use at least one letter other than numbers as the document name!')
						break
					else:	
						nodename.append(nexinline[0])
						tmp = nexinline[1]
						tmp = tmp.strip(';')
						if len(tmp) < 1:
							isnex = -6
							print ('Wrong nex format! No document contents')
							break
						nodelen.append(len(tmp))
		if isnex == 1:
			if len(set(nodename)) != len(nodename):
					isnex = -7
					print ('Wrong nex format! Repeated document names!')
			
			elif len(set(nodelen)) != 1:
					isnex = -8
					print ('Wrong nex format! Differnt lengths of documents!')
	
	return isnex
	
# print (checknex('test.nex'))
