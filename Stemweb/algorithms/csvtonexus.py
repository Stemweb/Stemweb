#!/usr/bin/python
import sys
import string

chars = list(string.ascii_letters) + list(string.digits) + [x for x in string.punctuation if x is not '?']

def csv2nex(csv_data):
        ''' Convert given csv file to nexus format.

                Parameters:

                csv_data        : Absolute filepath to the CSV formatted file with tabs as
                                          separators. The CSV file must be already aligned with '-'
                                          characters for missing data
                                  The first line of the data matrix contains a list of taxa names;
                                  related taxa are in the columns

                Transposes data matrix (rows2columns & columns2rows)

                Returns nexus format of the file as a list of lists, where first index
                of the list constains the name of the taxa and the rest of the list
                contains taxa.
        '''
        lines = csv_data.split('\n')
        taxas = [name.strip() for name in lines[0].split('\t')]
        data = {}
        for t in taxas: data[t] = ""

        for line in lines[1:]:
                        word_list = [ x.strip() for x in line.split('\t') ]
                        word_set = list(set(word_list) | set([""]))
                        word_set.sort()
                        for i,w in enumerate(word_list):
                                if w and w != "-" and w != "":
                                        data[taxas[i]] += chars[word_set.index(w) - 1]
                                else:
                                        data[taxas[i]] += "?"

        ret = "#NEXUS\nMATRIX\n"
        for c in taxas:
                ret += c + "\t" + data[c]  + "\n"
        ### workaround in py37; don't know yet when double backslashes come in:
        ret.replace('\\\\', '\\')        ### replace 2 backslashes by 1 backslash; each time escaped character
        return ret +";"
