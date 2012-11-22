#!/usr/bin/python

'''
Neighbor-Joining algorithm
implementation by Teemu Roos, March 2012
reads sequences in Nexus format from input
and prints out NJ tree in Newick format

Changed to subclass implementation of AlgorithmTask by Simo Linkola
in April 2012.
'''
import os
import sys
import logging
from Stemweb.algorithms.tasks import AlgorithmTask


# node structure for storing the tree
class Node:
	len = 0.0
	def __init__(self, label, left, right):
		self.label = label
		self.left = left
		self.right = right


class NJ(AlgorithmTask):
	
	
	def __init_run__(self, *args, **kwargs):
		AlgorithmTask.__init_run__(self, *args, **kwargs)
		if self.algorithm_run:
			self.algorithm_run.image = os.path.join(self.run_args['url_base'], '%s_nj.svg' % (os.path.splitext(os.path.basename(self.run_args['input_file']))[0]))
			self.algorithm_run.newick = os.path.join(self.run_args['url_base'], '%s_nj.tre' % (os.path.splitext(os.path.basename(self.run_args['input_file']))[0]))
			self.algorithm_run.save()
		self.hc = 0	
		
	def hamming(self,r,s):
		n=0
		diff=0
		for i in range(len(r)):
			if r[i] != '?' and s[i] != '?':
				n=n+1
			if r[i] != s[i]: diff=diff+1
		#if n == 0:
		#	return 0
		#print diff*1.0/n
		self.hc = self.hc + 1
		return diff*1.0/n
		
	def mean(self, l): 
		return sum(l)*1.0/len(l)
		
	# returns distance between groups g1 and g2
	def getgd(self,g1, g2):
		if g1<g2:
			a1=g1; a2=g2
		else:
			a1=g2; a2=g1
		return self.gd[tuple([tuple(a1)]+[tuple(a2)])]
		
		
	# stores/updates distance between groups g1 and g2
	def setgd(self,g1, g2, val):
		if g1<g2:
			a1=g1; a2=g2
		else:
			a1=g2; a2=g1
		self.gd[tuple([tuple(a1)]+[tuple(a2)])]=float(val)
	
	
	# evaluates average distance between groups g1 and g2
	def groupdistance(self,g1,g2): 
		return self.mean([self.getgd([t1],[t2]) for t1 in g1 for t2 in g2 if [t1]!=[t2]])
	
	
	# tree output subroutine, called recursively
	def _printtree(self, node, nw = ""):
		newick = nw
		if node.left != None:
			newick += "("
			newick += self._printtree(node.left, nw = '')
			newick += ","
			newick += self._printtree(node.right, nw = '')
			newick += ")"
		else:
			newick += "%s" % (node.label)
		if node.len != 0.0:
			newick += ":{}".format(node.len)
		return newick
		
	
	# tree output
	def save_tree(self, node):
		newick = self._printtree(node, '') + ";"
		nw_path = os.path.join(self.run_args['outfolder'], '%s_nj.tre' % (os.path.splitext(os.path.basename(self.run_args['input_file']))[0]))
		print newick
		f = None
		try: 
			f = open(nw_path, 'w')
			f.write(newick)
			f.close()
		except:
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun %s:%s could\'t write in file %s.' % (self.algorithm_run.algorithm.name, self.algorithm_run.id, nw_path))
			return -1 
		
		from Stemweb.algorithms.utils import newick2svg
		svg_path = os.path.join(self.run_args['outfolder'], '%s_nj.svg' % (os.path.splitext(os.path.basename(self.run_args['input_file']))[0]))
		newick2svg(nw_path, svg_path, branch_length = False, radial = True)		
			
	
	def __algorithm__(self, run_args = None):
		
		# simple Hamming distance

			
			
		outfolder = run_args['outfolder']

		tax=[]  # list of taxon labels
		data={} # sequences
		waitformatrix = True  # should we skip initial part until MATRIX segment?
		
		f = None
		try:
			f = open(run_args['input_file'], 'r')
		except:
			logger = logging.getLogger('stemweb.algorithm_run')
			logger.error('AlgorithmRun %s:%s could\'t open file in %s. Aborting run.' % (self.algorithm_run.algorithm.name, self.algorithm_run.id, run_args['input_file']))
			self._stop.value = 1
			return -1 	
						
					
		for line in f:
			if line.strip().upper()=="#NEXUS": waitformatrix=True
			if waitformatrix and line.strip().upper()!="MATRIX": continue
			if waitformatrix and line.strip().upper()=="MATRIX": waitformatrix=False; continue
			if line.strip()=="": continue
			if line.strip()==";": break
		
			t=line.split()[0]
			if t not in tax: # new taxon; create new data sequence
				tax.append(t)
				data[t]=line.split()[1]
			else:            # continuation of existing taxon; concatenate to existing seq.
				data[t]=data[t]+line.split()[1]
			if data[tax[-1]][-1]==';': data[tax[-1]]=data[tax[-1]][0:-1]; break # end matrix
		
		for dat in data.values():
			print len(dat)
		
		d={}                  # observed distances between pairs
		self.gd={}                 # distances between groups
		nodes={}              # created tree nodes (used to store NJ tree structure)
		taxa = len(tax)		# number of taxa
		print taxa

				
		# initialize tree structure and distances
		i = 0
		for tax1 in tax:
			nodes[tuple([tax1])] = Node(tax1,None,None)
			d[tax1,tax1]=0
			for tax2 in tax:
				i = i + 1
				d[tax1,tax2] = self.hamming(data[tax1], data[tax2])
				if (tax1,tax2) in d: # mirror distances given in example
					d[tax2,tax1]=d[tax1,tax2]
				# distances between singleton groups
				self.setgd(tuple([tax1]),tuple([tax2]),d[tax1,tax2])
		print i
		print self.hc
		
		# list of nodes to be combined (singletons will be replaced by
		# groups of manuscripts)
		S=[tuple([t]) for t in tax]
		
		# main loop
		while len(S)>1:
			# computer NJ distances
			njd={}
			# first evaluate r_i for each taxon
			r={}
			for g in S:
				if len(S)>2:
					r[g] = sum([self.getgd(g,other) for other in S if other!=g])/(len(S)-2)
				else:
					# on the last round N-2=0, so never mind
					r[g] = 0
			# evaluate NJ distances d_{i,j}-(r_i+r_j)
			for g1 in S:
				for g2 in S:
					if g1<g2:
						njd[g1,g2] = self.getgd(g1,g2)-(r[g1]+r[g2])
		
			# pick pair of nodes with minimum distance
			p=min(njd,key=njd.get) 
			# adjust edge lengths of the combined nodes
			nodes[p[0]].len = abs(.5*(self.getgd(p[0],p[1]) + r[p[0]] - r[p[1]]))
			nodes[p[1]].len = abs(.5*(self.getgd(p[0],p[1]) + r[p[1]] - r[p[0]]))
			# create a new node for the pair
			new=p[0]+p[1]
			# update tree structure by adding node with two children
			nodes[tuple(new)]=Node(tuple(new),nodes[p[0]],nodes[p[1]])
			# remove combined elements from the list of taxa 
			Snew=[g for g in S if g not in p]
			# add the new node in the distance matrix
			for other in Snew:
				self.setgd(new,other,.5*(self.getgd(p[0],other)+self.getgd(p[1],other)-
		                            self.getgd(p[0],p[1])))
			# ...and to the list of taxa
			S=Snew+[new]
			
		self.save_tree(nodes[tuple(new)])
		print nodes
		
		self._stop.value = 1
		
	
