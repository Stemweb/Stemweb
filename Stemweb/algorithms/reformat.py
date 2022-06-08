#!/usr/bin/python
import string
import csv


def re_format(input_data):
	''' TSV-parse input data and
		convert input_data from string format into a dictionary format
		and transpose the input as shown in this example:

	input example:
	"taxum-1 \t taxum-2 \t taxum-3 \t taxum-4\n
	Text1-line1 \t Text2-line1 \t Text3-line1 \t Text4-line1 \n		# line:  [Text1-line1 Text2-line1 Text3-line1 Text4-line1] // all texts - same (particular) line
	Text1-line2 \t Text2-line2 \t Text3-line2 \t Text4-line2 \n
	Text1-line3 \t Text2-line3 \t Text3-line3 \t Text4-line3"


	returns such a data-dictionary:
	{
	"taxum-1": "Text1-line1 \n Text1-line2 \n Text1-line3",			# dict value:  particular (same) text - all lines
	"taxum-2": "Text2-line1 \n Text2-line2 \n Text2-line3",	
	"taxum-3": "Text3-line1 \n Text3-line2 \n Text3-line3",
	"taxum-4": "Text4-line1 \n Text4-line2 \n Text4-line3"
	}

	'''

	data_dict = {}
	read_tsv = csv.DictReader(input_data.split('\n'), delimiter='\t')	### TSV-parsing
	taxas = read_tsv.fieldnames
	number_of_taxas = len(taxas)
	data_dict=dict.fromkeys(taxas, "")	### initialze keys in data_dict from taxas; init all values with ""
	for index, tax in enumerate(taxas):  # tax is each value in line 1
			for idx, row in enumerate(read_tsv, start=2): # row is the dictionary produced for each of lines 2-N
				#thisreading = row[tax] # thisreading is the cell value for the given tax at the given row
				particular_line_asList = list(row.values())		### .values() returns a view, rather than a list
				if number_of_taxas > len(particular_line_asList):
					expt = "format error: row " + str(idx) + " has fewer entries than line 1 which contains the taxas"
					#raise Exception(expt)
					return expt
				if number_of_taxas < len(particular_line_asList):
					expt = "format error: row " + str(idx) + " has more entries than line 1 which contains the taxas"
					#raise Exception(expt)
					return expt
				#particular_line_asList[:] = [x + '\n' for x in particular_line_asList]   ### add '\n' to each element in the list
				for c, key in enumerate(data_dict):
					data_dict[key]="\n".join( [data_dict[key],(particular_line_asList[c]) ])

	"""
	### previous solution ####
	tmp = ""
	elem = ""
	taxas = [name.strip() for name in tsv_parsed_content[0]]
	number_of_taxas = len(taxas)
	for tax in taxas: data_dict[tax] = ""
	number_of_texts = len(tsv_parsed_content[1])
	
	# check that each row in tsv_parsed_content has the same number of elements! else exit with an error message
	for row in range(1,len(tsv_parsed_content)):
		if number_of_taxas != len((tsv_parsed_content[row])):
			raise Exception("the number of taxa does not match the number of texts; or the number of texts is not the same in all lines") 

	for z in range(len(taxas)):
		for i in range(1,len(tsv_parsed_content)):  ### start with i = 1 because tsv_parsed_content[0] contains the taxa
			try:
				elem = (tsv_parsed_content[i]).pop(0)
			except IndexError as e:
				raise Exception(e)
			finally:
				tmp += (elem + '\n')
		data_dict[taxas[z]] = tmp
		tmp = ""
	"""

	return data_dict


	

