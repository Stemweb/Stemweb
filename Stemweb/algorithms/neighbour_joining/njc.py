#!/usr/bin/python
# Neighbor-Joining algorithm
# implementation by Teemu Roos, March 2012
# reads sequences in Nexus format from input
# and prints out NJ tree in Newick format

import logging
import sys, traceback
from time import sleep
from Stemweb.algorithms.tasks import AlgorithmTask
import Stemweb.algorithms.settings

# node structure for storing the tree
class Node:
    len = 0.0
    def __init__(self, label, left, right):
        self.label = label
        self.left = left
        self.right = right

class NJ(AlgorithmTask):
	name = 'Neighbour Joining'
	has_image = True
	has_newick = True
	has_networkx = False
	input_file_key = 'input_file'
		
	def __algorithm__(self, run_args = None):

		# simple Hamming distance
		def hamming(r,s):
		    #raise Exception(" This is an intended test case exception from NJ-algorithm")   ### a manual test case in order to call task.py/external_algorithm_run_error()
		    n=0
		    diff=0
		    for i in range(len(r)):
		        if r[i] != '?' and s[i] != '?':
		            n=n+1
		            if r[i] != s[i]: diff=diff+1
		    if n == 0: return 0
		    #print diff*1.0/n
		    return diff*1.0/n
		
		def mean(l): return sum(l)*1.0/len(l)
		
		# returns distance between groups g1 and g2
		def getgd(g1,g2):
		    if g1<g2:
		        a1=g1; a2=g2
		    else:
		        a1=g2; a2=g1
		    return gd[tuple([tuple(a1)]+[tuple(a2)])]
		
		# stores/updates distance between groups g1 and g2
		def setgd(g1,g2,val):
		    if g1<g2:
		        a1=g1; a2=g2
		    else:
		        a1=g2; a2=g1
		    gd[tuple([tuple(a1)]+[tuple(a2)])]=float(val)
		
		# evaluates average distance between groups g1 and g2
		def groupdistance(g1,g2): 
		    return mean([getgd([t1],[t2]) for t1 in g1 for t2 in g2 if [t1]!=[t2]])
		            
		# tree output subroutine, called recursively
		def _printtree(node, nw = ""):
			newick = nw
			if node.left != None:
				newick += "("
				newick += _printtree(node.left, nw = '')
				newick += ","
				newick += _printtree(node.right, nw = '')
				newick += ")"
			else:
				newick += "%s" % (node.label)
			if node.len != 0.0:
				newick += ":{0}".format(node.len)
			return newick
		
		# tree output
		def printtree(node):
		    print _printtree(node, '')
		    
		
		# tree output
		def save_tree(node):
			newick = _printtree(node, '') + ";"
			f = None
			try: 
				f = open(self.newick_path, 'w')
				f.write(newick)
				f.close()
			except:
				logger = logging.getLogger('stemweb.algorithm_run')
				logger.error('AlgorithmRun %s:%s could\'t write in file %s.' % \
				(self.algorithm_run.algorithm.name, self.algorithm_run.id, \
				self.newick_path))
				return -1 
			
			from Stemweb.algorithms.utils import newick2img
			newick2img(self.newick_path, self.image_path, \
				branch_length = False, radial = self.radial_image, width = 800)	
		
		f = None
		try:
			f = open(run_args['input_file'], 'r')
		except:
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun %s:%s could\'t open file in %s. Aborting run.' % \
			(self.algorithm_run.algorithm.name, self.algorithm_run.id, run_args['input_file']))
			self._stop.value = 1
			return -1 
		
		try:
			tax=[]  # list of taxon labels
			data={} # sequences
			waitformatrix=True  # should we skip initial part until MATRIX segment?
			
			for line in f:
				if line.strip().upper()=="#NEXUS": waitformatrix=True
				if waitformatrix and line.strip().upper()!="MATRIX": continue
				if waitformatrix and line.strip().upper()=="MATRIX": waitformatrix=False; continue
				if line.strip()=="": continue
				if line.strip()==";": break
			
				tax.append(line.strip().split()[0])
				data[tax[-1]]=line.strip().split()[-1]
				if data[tax[-1]][-1]==';': data[tax[-1]]=data[tax[-1]][0:-1]; break # end matrix
			
			#print "these Taxas", len(tax)
			#print len(data[tax[0]])
			#print len(data[tax[-1]])

			taxa=len(tax)         # number of taxa
			d={}                  # observed distances between pairs
			gd={}                 # distances between groups
			nodes={}              # created tree nodes (used to store NJ tree structure)
			
			# Example in Table 27.11 in evolution-textbook.org
			example = None # set to 1 or 2 to use one of the examples
			#example = 1 # set to 1 or 2 to use one of the examples
			if example == 1:
				tax=['A','B','C','D','E','F']
				d['A','B']=5
				d['A','C']=4
				d['A','D']=7
				d['A','E']=6
				d['A','F']=8
				d['B','C']=7
				d['B','D']=10
				d['B','E']=9
				d['B','F']=11
				d['C','D']=7
				d['C','E']=6
				d['C','F']=8
				d['D','E']=5
				d['D','F']=9
				d['E','F']=8
			elif example==2:
				tax=['A','B','C','D']
				d['A','B']=7; d['A','C']=11; d['A','D']=14
				d['B','C']=6; d['B','D']=9
				d['C','D']=7
			elif example==3:
				tax=['A','B','C','D']
				d['A','B']=2
				d['A','C']=4
				d['A','D']=5
				d['B','C']=4
				d['B','D']=5
				d['C','D']=3
			
			# initialize tree structure and distances
			for tax1 in tax:
				nodes[tuple([tax1])] = Node(tax1,None,None)
				d[(tax1,tax1)]=0
				for tax2 in tax:
					if not example:
						d[(tax1,tax2)] = hamming(data[tax1], data[tax2])
					if (tax1,tax2) in d: # mirror distances given in example
						d[(tax2,tax1)]=d[(tax1,tax2)]
					# distances between singleton groups
					setgd(tuple([tax1]),tuple([tax2]),d[(tax1,tax2)])
					
			# list of nodes to be combined (singletons will be replaced by
			# groups of manuscripts)
			S=[tuple([t]) for t in tax]
			
			#print "S", len(S)
			# main loop
			while len(S)>1:
				# computed NJ distances
				njd={}
				# first evaluate r_i for each taxon
				r={}
				for g in S:
					if len(S)>2:
						r[g] = sum([getgd(g,other) for other in S if other!=g])/(len(S)-2)
					else:
						# on the last round N-2=0, so never mind
						r[g] = 0
				# evaluate NJ distances d_{i,j}-(r_i+r_j)
				for g1 in S:
					for g2 in S:
						if g1<g2:
							njd[g1,g2] = getgd(g1,g2)-(r[g1]+r[g2])
			
				# pick pair of nodes with minimum distance
				p=min(njd,key=njd.get) 
				# adjust edge lengths of the combined nodes
				nodes[p[0]].len = abs(.5*(getgd(p[0],p[1]) + r[p[0]] - r[p[1]]))
				nodes[p[1]].len = abs(.5*(getgd(p[0],p[1]) + r[p[1]] - r[p[0]]))
				# create a new node for the pair
				new=p[0]+p[1]
				# update tree structure by adding node with two children
				nodes[tuple(new)]=Node(tuple(new),nodes[p[0]],nodes[p[1]])
				# remove combined elements from the list of taxa 
				Snew=[g for g in S if g not in p]
				# add the new node in the distance matrix
				for other in Snew:
					setgd(new,other,.5*(getgd(p[0],other)+getgd(p[1],other)-
										getgd(p[0],p[1])))
				# ...and to the list of taxa
				S=Snew+[new]
				#if len(S) == 2:
				#	sleep(50)   ### test_case: simulate long lasting nj-algorithm run in order to call task.py/external_algorithm_run_error()
				#	### following an error test case combined with above long lasting calculation :
				#	raise Exception("This is an intended test case exception from almost the end of the NJ-algorithm")   

			
			


			# print out tree
			save_tree(nodes[tuple(new)])
			
			self._stop.value = 1

		except: # catch *all* exceptions
			#typ =  sys.exc_info()[0]		# e.g.: <type 'exceptions.Exception'>
			value = sys.exc_info()[1]		# e.g.: This is an intended test case exception from NJ-algorithm
			ex_type, ex, tb = sys.exc_info()
			#traceback.print_exc()
			#traceback.print_tb(tb)
			trace_back = traceback.format_tb(tb)   # get  traceback info as string 
			self.algorithm_run.error_msg = 	value # = ex? ; keep only the error message; not the detailed tb traceback info
			self.algorithm_run.status = Stemweb.algorithms.settings.STATUS_CODES['failure']
			self.algorithm_run.save()
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun %s:%s aborted with this error: %s  and this traceback: %s ' % \
			(self.algorithm_run.algorithm.name, self.algorithm_run.id, value, trace_back))
			self._stop.value = 1
			return -1
		#finally: 
			#del tb

