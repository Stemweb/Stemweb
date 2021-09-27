#!/usr/bin/python
import string


def re_format(input_data):
	''' Convert given input_data from string format into a dictionary format

	input example:
	"taxum-1 \t taxum-2 \t taxum-3 \t taxum-4\n
	Text1-line1 \t Text2-line1 \t Text3-line1 \t Text4-line1 \n		# word_list
	Text1-line2 \t Text2-line2 \t Text3-line2 \t Text4-line2 \n
	Text1-line3 \t Text2-line3 \t Text3-line3 \t Text4-line3"


	returns such a data-dictionary:
	{
	"taxum-1": "Text1-line1 \n Text1-line2 \n Text1-line3",			# dict value: tmp 
	"taxum-2": "Text2-line1 \n Text2-line2 \n Text2-line3",	
	"taxum-3": "Text3-line1 \n Text3-line2 \n Text3-line3",
	"taxum-4": "Text4-line1 \n Text4-line2 \n Text4-line3"
	}

	'''
	
	
	lines = input_data.split('\n')
	taxas = [name.strip() for name in lines[0].split('\t')]

	data_dict = {}
	for tax in taxas: data_dict[tax] = ""

	tmp = ""	
	word_list = [] 

	for line in lines[1:]:
		word_list.append(line.split('\t'))
	
	for z in range(len(taxas)):
		for i in range(len(word_list)):
			tmp += ((word_list[i]).pop(0) + '\n')
		data_dict[taxas[z]] = tmp
		tmp = ""

	return data_dict


	

