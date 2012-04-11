'''
Created on Apr 10, 2012

@author: slinkola
'''
import sys
import logging
from Stemweb.algorithms.stoppable_algorithm import StoppableAlgorithm

# node structure for storing the tree
class Node:
    len = 0.0
    def __init__(self, label, left, right):
        self.label = label
        self.left = left
        self.right = right


class NJ(StoppableAlgorithm):
	
	
	def __init__(self, *args, **kwargs):
		StoppableAlgorithm.__init__(self, *args, **kwargs)
		print self.run_args
	
	
	def __algorithm__(self, run_args = None):	          
		d={}                  # observed distances between pairs
		gd={}                 # distances between groups
		nodes={}              # created tree nodes (used to store NJ tree structure)
		tax=[]  # list of taxon labels
		data={} # sequences
		waitformatrix = True  # should we skip initial part until MATRIX segment?
		
		f = None
		try:
			f = open(run_args['input_file'], 'r')
		except:
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun %s:%s could\'t open file in %s. Aborting run.' % (self.algorithm_run.algorithm.name, self.algorithm_run.id, run_args['input_file']))
			return -1 	
			
			
		for line in f.readlines():
			#if line.strip().upper() == "#NEXUS": 
			#	waitformatrix = True
			if waitformatrix and line.strip().upper() != "MATRIX": 
				continue
			if waitformatrix and line.strip().upper() == "MATRIX": 
				waitformatrix = False
				continue
			if line.strip() == ";": 
				break
			tax.append(line.strip().split()[0])
			data[tax[-1]] = line.strip().split()[-1]
			if data[tax[-1]][-1] == ';': 
				data[tax[-1]] = data[tax[-1]][0:-1]
				break
		
		taxa = len(tax)		# number of taxa
		
		# simple Hamming distance
		def hamming(r,s):
		    n=0
		    diff=0
		    for i in range(len(r)):
		        if r[i] != '?' and s[i] != '?':
		            n=n+1
		            if r[i] != s[i]: diff=diff+1
			if n == 0:
				return 0
		    return diff*1.0/n
			
		def mean(l): 
			return sum(l)*1.0/len(l)
			
		# returns distance between groups g1 and g2
		def getgd(g1, g2):
		    if g1<g2:
		        a1=g1; a2=g2
		    else:
		        a1=g2; a2=g1
		    return gd[tuple([tuple(a1)]+[tuple(a2)])]
			
			
		# stores/updates distance between groups g1 and g2
		def setgd(g1, g2, val):
		    if g1<g2:
		        a1=g1; a2=g2
		    else:
		        a1=g2; a2=g1
		    gd[tuple([tuple(a1)]+[tuple(a2)])]=float(val)
		    
		    
		# evaluates average distance between groups g1 and g2
		def groupdistance(g1,g2): 
		    return mean([getgd([t1],[t2]) for t1 in g1 for t2 in g2 if [t1]!=[t2]])
		   
		   
		# tree output subroutine, called recursively
		def _printtree(node):
		    if node.left != None:
		        sys.stdout.write("(")
		        _printtree(node.left)
		        sys.stdout.write(",")
		        _printtree(node.right)
		        sys.stdout.write(")")
		    else:
		        sys.stdout.write(node.label)
		    if node.len != 0.0:
		        sys.stdout.write(":{}".format(node.len))
		
		
		# tree output
		def printtree(node):
		    _printtree(node)
		    print
			
		# initialize tree structure and distances
		for tax1 in tax:
		    nodes[tuple([tax1])] = Node(tax1,None,None)
		    d[tax1,tax1]=0
		    for tax2 in tax:
		        d[tax1,tax2] = hamming(data[tax1], data[tax2])
		        if (tax1,tax2) in d: # mirror distances given in example
		            d[tax2,tax1]=d[tax1,tax2]
		        # distances between singleton groups
		        setgd(tuple([tax1]),tuple([tax2]),d[tax1,tax2])
			
		# list of nodes to be combined (singletons will be replaced by
		# groups of manuscripts)
		S = [tuple([t]) for t in tax]	
		
		# Main loop
		while len(S)>1:
			# computer NJ distances
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
			nodes[p[0]].len = .5*(getgd(p[0],p[1]) + r[p[0]] - r[p[1]])
			nodes[p[1]].len = .5*(getgd(p[0],p[1]) + r[p[1]] - r[p[0]])
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
			
		printtree(nodes[tuple(new)])
		
		self._stop.value = 1
		
	
