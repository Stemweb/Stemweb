'''
	Neighbor net algorithm implementation as child class of AlgorithmTask.
'''

#!/usr/bin/python
#-----------------------------------------------------------------
# NeighborNet algorithm
# implementation by Teemu Roos, April 2012
# reads sequences in Nexus format from input
# and plots NeighborNet in a PDF file

import os
import sys
import math
import logging

import scipy.optimize
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

from Stemweb.algorithms.tasks import AlgorithmTask


class NN(AlgorithmTask):
	name = "Neighbour Net"
	score_name = 'score'
	
	def __init_run__(self, *args, **kwargs):
		AlgorithmTask.__init_run__(self, *args, **kwargs)
		if self.algorithm_run:
			self.algorithm_run.score = 0
			self.image_path = os.path.join(self.run_args['outfolder'], 'nn_network.png')
			self.algorithm_run.save()

	def __algorithm__(self, run_args = None):

		# simple Hamming distance
		def hamming(r,s):
		    n=0
		    diff=0
		    for i in range(len(r)):
		        if r[i] != '?' and s[i] != '?':
		            n=n+1
		            if r[i] != s[i]: diff=diff+1
		    if n==0: return 0
		    return diff*1.0/n
		
		def mean(l): return sum(l)*1.0/len(l)
		
		def norm(v): return math.sqrt(sum([x*x for x in v]))
		
		def pos_dist(a,b): return norm([a[0]-b[0],a[1]-b[1]])
		
		# returns distance between taxa t1 and t2
		def getF(t1,t2):
		    # sort alphabetically to avoid asking for (t1,t2) when have (t2,t1)
		    if (t1,)<(t2,):
		        a1=(t1,); a2=(t2,)
		    else:
		        a1=(t2,); a2=(t1,)
		    return F[(a1,a2)]
		
		# stores/updates distance between taxa t1 and t2
		def setF(t1,t2,val):
		    if (t1,)<(t2,):
		        a1=(t1,); a2=(t2,)
		    else:
		        a1=(t2,); a2=(t1,)
		    F[(a1,a2)]=float(val)
		
		# evaluates average distance between clusters g1 and g2
		def groupdistance(g1,g2): 
		    return mean([getF(t1,t2) for t1 in g1 for t2 in g2])
		
		# removes taxon y from the set of taxa and updates distance matrix F
		def remove(x,y,z):
		    self.tax
		    self.tax=[s for s in self.tax if s!=y]
		    for w in self.tax:
		        if w != z and w != x:
		            setF(x,w,2.0/3.0*getF(x,w)+1.0/3.0*getF(y,w))
		            setF(z,w,2.0/3.0*getF(z,w)+1.0/3.0*getF(y,w))
		    setF(x,z,1.0/3.0*(getF(x,y)+getF(x,z)+getF(y,z)))
		            
		self.tax=[]  # list of taxon labels
		data={} # sequences
		waitformatrix=True  # should we skip initial part until MATRIX segment?
		
		if run_args:
			f = None
			try: 
				f = open(run_args['input_file'], 'r')
			except:
				logger = logging.getLogger('stemweb.algorithm_run')
				logger.error('AlgorithmRun %s:%s could\'t open file in %s. Aborting run.'  %  \
				(self.algorithm_run.algorithm.name, self.algorithm_run.id, run_args['input_file']))
				return -1 	
		
			for line in f.readlines():
			    #if line.strip().upper()=="#NEXUS": waitformatrix=True
			    if waitformatrix and line.strip().upper()!="MATRIX": continue
			    if waitformatrix and line.strip().upper()=="MATRIX": 
			        waitformatrix=False; continue
			    if line.strip()=="": continue
			    if line.strip()==";": break
			
			    line=line.strip()
			    t=line.split()[0]
			
			    if t not in self.tax: # new taxon; create new data sequence
			        self.tax.append(t)
			        data[t]=line.split()[1]
			    else:
			        # continuation of existing taxon; concatenate to existing seq.
			        data[t]=data[t]+line.split()[1]
			
			    if data[self.tax[-1]][-1]==';': # end matrix
			        data[self.tax[-1]]=data[self.tax[-1]][0:-1]; 
			        break 
		
		d={}                  # observed distances between pairs
		F={}                  # updated pairwise distance matrix
		neigh={}              # store ordering of nodes as pairs (alphabetically)
		
		example = None # set to the number of example or None
		if example == 1:
		    # Example in Table 27.11 in evolution-textbook.org
		    self.tax=['A','B','C','D','E','F']
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
		elif example == 2:
		    # small example where distances are not compatible with any tree
		    # but a network (where middle branch becomes a rectangle) gives
		    # perfect fit
		    self.tax=['A','B','C','D']
		    d['A','B']=2
		    d['A','C']=3
		    d['A','D']=5
		    d['B','C']=4
		    d['B','D']=5
		    d['C','D']=3
		
		taxa=len(self.tax)         # number of taxa
		
		# initialize distance matrix F
		for tax1 in self.tax:
		    d[tax1,tax1]=0
		    for tax2 in self.tax:
		        if not example:
		            d[tax1,tax2] = hamming(data[tax1], data[tax2])
		        if (tax1,tax2) in d: # mirror distances given in example
		            d[tax2,tax1]=d[tax1,tax2]
		        # distances between singleton groups
		        setF(tax1,tax2,d[tax1,tax2])
		
		#--------------------------------------------------------------------
		# Phase 1: Pair nodes to create a circular order
		
		# list of clusters to be combined (singletons will be replaced by pairs)
		S=[(t,) for t in self.tax]
		
		# main loop
		while len(S)>1:
		    # compute same distances as in Neighbor-Joining.
		    # first evaluate r_i for each node
		    if len(S)>2:
		        r={g:sum([groupdistance(g,other) for other in S if other!=g])\
		               /(len(S)-2) for g in S}
		    else:
		        # on the last round N-2=0, so never mind
		        r={g:0 for g in S}
		    # pick pair of clusters with minimum distance (such that if one of them
		    # is single and other is couple, the first one is the single; hence
		    # len(g1)<=len(g2).)
		    njd={(g1,g2,):groupdistance(g1,g2)-(r[g1]+r[g2]) \
		             for g1 in S for g2 in S \
		             if len(g1)<len(g2) or (len(g1)==len(g2) and (g1,)<(g2,))}
		    p=min(njd,key=njd.get)
		
		    # find x in p[0] and y in p[1] that are closest to one another.
		    # first temporarily uncouple both clusters
		    tempS = [g for g in S if g not in p]+\
		        [(t,) for t in p[0]]+[(t,) for t in p[1]]
		    if len(tempS)>2:
		        rtemp={(t,):sum([groupdistance([t],other) for other in tempS \
		                                   if other!=(t,)])/(len(tempS)-2) \
		                   for t in p[0]+p[1]}
		    else:
		        # on the last round N-2=0, so never mind about the r's
		        rtemp={(t,):0 for t in p[0]+p[1]}
		    # evaluate NJ distances d_{i,j}-(r_i+r_j)
		    pd={(x,y):getF(x,y)-(rtemp[(x,)]+rtemp[(y,)]) \
		            for x in p[0] for y in p[1]}
		    # x and y are now obtained by picking smallest distance from pd
		    xy=min(pd,key=pd.get)
		    x=xy[0]; y=xy[1]
		
		    # set x and y as neighbors
		    neigh[x,y]=True;
		
		    # three cases depending on whether combined groups are singletons or pairs
		    if len(p[0])==1 and len(p[1])==1:
		        # case M1: single+single
		        S=[g for g in S if g not in p]+[p[0]+p[1]]
		    if len(p[0])==1 and len(p[1])==2:
		        # case M2: single+couple
		        # let z be the taxon in the couple which is not y
		        z=[z for z in p[1] if z!=y][0]
		        S=[g for g in S if g not in p]+[(x,)+(z,)]
		        remove(x,y,z)
		    if len(p[0])==2 and len(p[1])==2:
		        # case M3: couple+couple
		        # let w be the taxon in the first couple which is not x
		        w=[w for w in p[0] if w!=x][0]
		        # let z be the taxon in the second couple which is not y
		        z=[z for z in p[1] if z!=y][0]
		        S=[g for g in S if g not in p]+[(w,)+(z,)]
		        remove(x,y,z)
		        remove(w,x,z)
		
		# add a final link between the last two remaining nodes to make
		# the ordering circular
		neigh[tuple([S[0][0]]),tuple([S[0][1]])]=True
		
		# construct the circular order from the pairs
		
		prev=None
		cur= self.tax[0]
		O = [cur]
		for i in range(taxa-1):
		    next=([key[0] for key in neigh if key[1]==cur and key[0]!=prev]+\
		              [key[1] for key in neigh if key[0]==cur and key[1]!=prev])[0]
		    prev=cur
		    cur=next
		    O = O + [cur]
		
		# construct set of allowed splits S from circular order
		# (important that they are in order of non-increasing cardinality of the
		# split part that doesn't contain taxon x_i (the first taxon in the circular
		# order O); see the Circular network algorithm (Alg 7.2.1) in Huson et 
		# al. (2010)
		
		Sp = [(p,q) for p in range(1,taxa) for q in range(p,taxa)]
		Sp = sorted(Sp, key=lambda sp: sp[0]-sp[1]) # what ho lambda!
		
		#--------------------------------------------------------------------
		# Phase 2: Estimate split weights
		
		# construct vector d with all pairwise distances
		d_obs = [d[O[i],O[j]] for i in range(taxa) for j in range(i+1,taxa)]
		
		# construct indicator matrix A from splits compatible with circular order
		def separated(i,j,t):
		    return ((i<t[0] or i>t[1]) and j>=t[0] and j<=t[1]) or \
		        (i>=t[0] and i<=t[1] and (j<t[0] or j>t[1]))
		A = [[1 if separated(i,j,sp) else 0 for sp in Sp] \
		         for i in range(taxa) for j in range(i+1,taxa)]
		
		# obtain split weights by solving a non-negative least squares problem
		(x_estim,resid)=scipy.optimize.nnls(A,d_obs)
		
		# associate estimated weights to splits
		Sx = {Sp[i]:x_estim[i] for i in range(len(Sp))}
		
		#--------------------------------------------------------------------
		# Phase 3: represent obtained set of splits as a SplitNetwork
		
		# start with a star graph
		
		G=nx.Graph()
		pos={}; lab={}; edg_lab={}
		mass={}
		G.add_node(0); pos[0]=(0,0); lab[0]=""
		angle=0 # first node at 3 o'clock (0 radians)
		for t in range(len(O)):
		    # trivial split for node x_i is given as (x_2,...,x_n)
		    if t==0: l=Sx[(1,len(O)-1)] 
		    # trivial split for nodes x_i, i>1 are given as (x_i)
		    else: l=Sx[t,t] 
		    G.add_node(O[t]); pos[O[t]]=(math.cos(angle)*l,math.sin(angle)*l)
		    mass[O[t]]=(math.cos(angle),math.sin(angle))
		    lab[O[t]]=O[t]
		    angle=angle+2.0*math.pi/len(O) # orient leafs in circular order clock-wise
		    G.add_edge(0,O[t])
		    edg_lab[(0,O[t])]=pos_dist(pos[0],pos[O[t]])
		
		# now start adding splits one by one, with the size of the split part
		# including x_1 non-increasing (they are already sorted this way in Sp)
		
		plt.figure(figsize=(10,10)) # initialize figure environment
		
		c=1
		for sp in Sp+[None]:
		    if sp==None or (sp[1]-sp[0]>0 and sp[1]-sp[0]<len(O)-2 and Sx[sp]>0):
		#        plt.subplot(5,5,c)
		#        nx.draw(G,pos=pos,labels=lab,edge_labels=edg_lab,\
		#                    node_size=.1,font_size=4,width=.2,title=c)
		        if sp==None: 
		            break
		        c=c+1
		        if c>5*5: c=1
		        # exclude trivial splits
		        # find shortest path connecting end-points of split, x_p, x_q
		        # which also "touches" each of the other nodes in the split
		        # x_{p+1},...,x_{q-1}
		        splitpart=[O[i] for i in range(sp[0],sp[1]+1)]
		
		        # pathnodes will contain nodes that need to be duplicated to
		        # create a new split
		        pathnodes=[]
		        for i in range(sp[0]+1,sp[1]+1):
		            path=nx.shortest_path(G,source=O[i-1],target=O[i])[1:-1]
		            pathnodes=pathnodes+[pn for pn in path if pn not in pathnodes]
		
		        # duplicate nodes
		        prev=None
		        for n in pathnodes:
		            newnode = G.number_of_nodes()
		            pos[newnode] = pos[n]
		            G.add_node(newnode)
		
		            # update links (some edges will remain at the old node, some
		            # are changed to the newly created one
		            for nbr in list(G.neighbors(n)):
		                if nbr not in splitpart and nbr not in pathnodes:
		                    G.remove_edge(n,nbr)
		                    G.add_edge(newnode,nbr)
		                    edg_lab[(newnode,nbr)]=pos_dist(pos[newnode],pos[nbr])

		            # add edge between old and new node
		            G.add_edge(n, newnode)
		            edg_lab[(n,newnode)]=pos_dist(pos[n],pos[newnode])
		
		            # add edge between new nodes along the duplicated path
		            if prev: 
		                G.add_edge(newnode, prev)
		                edg_lab[(newnode,prev)]=pos_dist(pos[newnode],pos[prev])
		            prev=newnode
		
		        # move nodes included in the path, as well as nodes included
		        # in the split, away from the rest of the nodes
		        move_nodes = pathnodes+splitpart
		
		        # compute vector giving the angle to which the nodes are moved
		        # based on the angle to which the nodes in each split part were
		        # pointing in the star graph in the beginning
		        mass_cent_l_x = mean([mass[n][0] for n in splitpart])
		        mass_cent_l_y = mean([mass[n][1] for n in splitpart])
		        mass_cent_r_x = mean([mass[n][0] for n in set(O) - set(splitpart)])
		        mass_cent_r_y = mean([mass[n][1] for n in set(O) - set(splitpart)])
		        vector = [mass_cent_r_x-mass_cent_l_x,mass_cent_r_y-mass_cent_l_y]
		        vector = [x/norm(vector) for x in vector]
		
		        # update positions
		        for n in move_nodes:
		            pos[n] = [pos[n][i]-vector[i]*Sx[sp] for i in range(2)]
		
		# draw graph
		nx.draw(G,pos=pos,labels=lab,edge_labels=edg_lab,\
		            node_size=.1,font_size=8,width=.2,title=c)
		plt.savefig(self.image_path)
		
		# print diagnostic output
		d_var=mean([x*x for x in d_obs])
		d_estim = np.matrix(A) * np.matrix(x_estim).transpose()
		res_var=mean([(d_obs[i]-d_estim[i])**2 for i in range(len(d_obs))])
		# fit value describing how well distances in the network match actual ones
		fit_value =  (math.sqrt(d_var)-math.sqrt(res_var))/math.sqrt(d_var)
		self._put_in_results_({'score': fit_value })
		
		self._stop.value = 1
