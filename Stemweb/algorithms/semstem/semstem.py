from numpy import *
import time
import random
import os
import copy
import sys
import logging

from Stemweb.algorithms.tasks import AlgorithmTask
from Stemweb.algorithms.utils import newick2img

class Semstem(AlgorithmTask):
	name = "Semstem"
	has_newick = True
	
	def __init_run__(self, *args, **kwargs):
		AlgorithmTask.__init_run__(self, *args, **kwargs)
		if self.algorithm_run:
			self.algorithm_run.image = os.path.join(self.run_args['url_base'], 'tree', 'treebest.png')
			self.algorithm_run.newick = os.path.join(self.run_args['url_base'], 'tree', 'treebest.tre')
			self.image_path = os.path.join(self.run_args['outfolder'], 'tree', 'treebest.png')
			self.newick_path = os.path.join(self.run_args['outfolder'], 'tree', 'treebest.tre')
			self.algorithm_run.save()
		self.score_name = 'qscore'
		#self.iteration_name = 'iter'
		
	def __algorithm__(self, run_args):

		def createnode(treedic,node):
			treedic[node]={}
			treedic[node]['parent']=[]
			treedic[node]['child']=[]
			treedic[node]['neighbor']=[]
		
		def addedge(treedic,parent,child):
			treedic[child]['parent'].append(parent)
			treedic[child]['neighbor'].append(parent)
			
			treedic[parent]['child'].append(child)
			treedic[parent]['neighbor'].append(child)
			
		def removeedge(treedic,parent,child):
			treedic[child]['parent'].remove(parent)
			treedic[child]['neighbor'].remove(parent)
			treedic[parent]['child'].remove(child)
			treedic[parent]['neighbor'].remove(child)
		
		def removehidden(nodehiddenori,treedicori):
			treedic = copy.deepcopy(treedicori)
			nodehidden = list(nodehiddenori)
			finnish = 0
			while (finnish == 0):
				finnish = 1
				for nodei in nodehidden:
					if len(treedic[nodei]['neighbor'])==2:
						finnish = 0
						nodehidden.remove(nodei)
						if len(treedic[nodei]['child'])==2: # root
							childi = treedic[nodei]['child'][0]
							childj = treedic[nodei]['child'][1]
							addedge(treedic,childi,childj)
							removeedge(treedic,nodei,childi)
							removeedge(treedic,nodei,childj)
							del treedic[nodei]
							
						if len(treedic[nodei]['child'])==1: # not root
							childi = treedic[nodei]['child'][0]
							parenti = treedic[nodei]['parent'][0]
							addedge(treedic,parenti ,childi)
							removeedge(treedic,nodei,childi)
							removeedge(treedic,parenti ,nodei)
							del treedic[nodei]
					else:		
						if len(treedic[nodei]['neighbor'])==1:
							finnish = 0
							nodehidden.remove(nodei)
							if len(treedic[nodei]['parent'])==1:
								parenti = treedic[nodei]['parent'][0]
								removeedge(treedic,parenti ,nodei)
								del treedic[nodei]
							else:
								childi = treedic[nodei]['child'][0]
								removeedge(treedic,nodei, childi)
								del treedic[nodei]
			return treedic, nodehidden
			
		def readfile(inputfile):
			import re
			#readfile('heinrichi.nex')
			import math
			file = open(inputfile,'r')
			nexdata = file.read()
			nexdata = nexdata.replace('-','?')
			nexdata = nexdata.replace(' ','\t')
			file.close()
			
			nexdata = nexdata.split('\n')
			for i in range(len(nexdata)):
				if len(re.findall(r'matrix',nexdata[i].lower()))>0:
					startline = i+1
			for i in range(len(nexdata)-1,-1,-1):
				if len(re.findall(r'end',nexdata[i].lower()))>0:
					endline = i	
			nexdata = nexdata[startline:endline]
		
			namelist = {}
			datalist = []
			textdata = {}
			nodenumber = len(nexdata)
			
			index = 0
			for nexdatai in nexdata:
				nexdatai = nexdatai.strip()
				nexdatai = nexdatai.strip(';')
				nexdatai = nexdatai.split('\t',1)
				namelist[nexdatai[0].strip()] = index
				index = index+1
				textdatai = nexdatai[1].strip()
				textdata[nexdatai[0].strip()] = textdatai
				textlen = len(textdatai)
				if len(datalist)==textlen:
					for i in range(textlen):
						datalist[i].append(textdatai[i])	
				else:
					for i in range(textlen):
						datalist.append([textdatai[i]])
		
			datadic = {}
			dataori = []
			for datalisti in datalist:
				if '?' in datalisti:
					temp = list(set(datalisti))
					temp.remove('?')
					uniquenumber = len(temp)
				else:
					uniquenumber = len(list(set(datalisti)))
				
				if len(list(set(datalisti))) == 1:
					datalist.remove(datalisti)
				else:		
					chardic = {'?':'?'}
					j = 0
					letters = 'abcdefghijklmnopqrstuvwxyz'
					datalistrefinei = []
					for i in datalisti:
						if i in chardic.keys():
							datalistrefinei.append(chardic[i])
						else:
							datalistrefinei.append(letters[j-int(26*(math.floor(j/26)))])
							chardic[i]=letters[j-int(26*(math.floor(j/26)))]
							j=j+1
					dataori.append(datalistrefinei)
					if uniquenumber in datadic.keys():
						datadic[uniquenumber].append(datalistrefinei)
					else:
						datadic[uniquenumber]=[datalistrefinei]
			return (namelist ,datadic, textdata)
		
		def	njtree (textdata):
			import copy
			
			def countdiff(text1,text2):
				textlen = len(text1)
				j=0
				for i in range(textlen):
					if text1[i]=='?' or text2[i]=='?':
						j = j+0.1
					elif text1[i]!=text2[i]:
						j = j+1
				return j
				
			def ajustmatrix(distmatrix):
				distmatrix1 = copy.deepcopy(distmatrix)
				namelist = list(distmatrix1.keys())
				netdivergence = {}
				namenumber = len(namelist)
				for namei in namelist:
					disti = list(distmatrix1[namei].values())
					netdivergence[namei] = sum(disti)
				
				for namei in range(namenumber):
					for namej in range(namei+1,namenumber):
						distmatrix1[namelist[namei]][namelist[namej]] = distmatrix1[namelist[namei]][namelist[namej]]-((netdivergence[namelist[namei]]+netdivergence[namelist[namei]])/(namenumber-2))	
						distmatrix1[namelist[namej]][namelist[namei]] = distmatrix1[namelist[namei]][namelist[namej]]
				return (distmatrix1)
			
			def updatematrix(distmatrix,edgelengthdic,linkednodes,newnode):
				namelist = list(distmatrix.keys())
				distmatrix[newnode] = {}		
				edgelengthdic[(linkednodes[0],newnode)] = (distmatrix[linkednodes[0]][linkednodes[1]]/2)+((sum(distmatrix[linkednodes[0]].values())-sum(distmatrix[linkednodes[1]].values()))/(2*(len(namelist)-2)))
				edgelengthdic[(newnode,linkednodes[0])] = edgelengthdic[(linkednodes[0],newnode)]
				edgelengthdic[(linkednodes[1],newnode)] = distmatrix[linkednodes[0]][linkednodes[1]]-edgelengthdic[(linkednodes[0],newnode)]
				edgelengthdic[(newnode,linkednodes[1])] = edgelengthdic[(linkednodes[1],newnode)]
		
				distmatrix[newnode]={}
				for nodei in namelist:
					if nodei not in linkednodes:
						distmatrix[nodei][newnode]=(distmatrix[nodei][linkednodes[0]]+distmatrix[nodei][linkednodes[1]]-distmatrix[linkednodes[0]][linkednodes[1]])/2
						distmatrix[newnode][nodei]=distmatrix[nodei][newnode]
						del distmatrix[nodei][linkednodes[0]]
						del distmatrix[nodei][linkednodes[1]]
				
				for nodei in linkednodes:
					del distmatrix[nodei]
			
			
			def findnearestnode(distmatrix):
				namelist = list(distmatrix.keys())
				mindist = float('Inf')
				for namei in namelist:
					for namej in namelist:
						if namei != namej:
							if mindist > distmatrix[namei][namej]:
								mindist = distmatrix[namei][namej]
								nearestnode = [namei,namej]
				return (nearestnode,mindist)
					
			
			distmatrix = {}
			namelist = list(textdata.keys())
		
			for namei in namelist:
				distmatrix[namei] = {}
			for namei in range(len(namelist)):
				for namej in range((namei+1),len(namelist)):
					distmatrix[namelist[namei]][namelist[namej]] = countdiff(textdata[namelist[namei]],textdata[namelist[namej]])
					distmatrix[namelist[namej]][namelist[namei]] = distmatrix[namelist[namei]][namelist[namej]]
		
			hiddennodecount = 1	
			treedic = {}
			edgelengthdic = {}
			nodeorder = []
			nodehidden = []
			nodeleaf = list(distmatrix.keys())
			
			while len(distmatrix.keys())>2:
				distmatrixnormalized = ajustmatrix(distmatrix)
				nearestnode, mindist = findnearestnode(distmatrixnormalized)
				if nearestnode[0] not in treedic:
					createnode(treedic,nearestnode[0])
					nodeorder.append(nearestnode[0])	
				if nearestnode[1] not in treedic:
					createnode(treedic,nearestnode[1])
					nodeorder.append(nearestnode[1])
				if str(hiddennodecount) not in treedic:
					createnode(treedic,str(hiddennodecount))
					nodeorder.append(str(hiddennodecount))
					nodehidden.append(str(hiddennodecount))
			
				addedge(treedic,str(hiddennodecount),nearestnode[0])
				addedge(treedic,str(hiddennodecount),nearestnode[1])
				updatematrix(distmatrix,edgelengthdic,nearestnode,str(hiddennodecount))
				hiddennodecount = hiddennodecount+1
			noderemain = list(distmatrix.keys())
			if str(hiddennodecount) not in treedic:
				createnode(treedic,str(hiddennodecount))
				nodehidden.append(str(hiddennodecount))
		
			if noderemain[0] not in treedic:
				createnode(treedic,noderemain[0])
				nodeorder.append(noderemain[0])	
			if noderemain[1] not in treedic:
				createnode(treedic,noderemain[1])
				nodeorder.append(noderemain[1])
			addedge(treedic,str(hiddennodecount),noderemain[0])
			addedge(treedic,str(hiddennodecount),noderemain[1])
			edgelengthdic[(noderemain[0],str(hiddennodecount))] = distmatrix[noderemain[0]][noderemain[1]]/2 
			edgelengthdic[(str(hiddennodecount),noderemain[0])] = edgelengthdic[(noderemain[0],str(hiddennodecount))]
			edgelengthdic[(noderemain[1],str(hiddennodecount))] = edgelengthdic[(noderemain[0],str(hiddennodecount))]
			edgelengthdic[(str(hiddennodecount),noderemain[1])] = edgelengthdic[(noderemain[0],str(hiddennodecount))]
			treeroot = str(hiddennodecount)
			nodeorder.append(treeroot)
			
			return (treeroot, nodeorder, nodehidden, nodeleaf, treedic)
		
		def nohiddeninitial(textdata):
			namelist = list(textdata.keys())
			treeroot = namelist[0]
			nodeleaf = [namelist[-1]]
			nodehidden = []
			nodeorder = [treeroot]
			treedic = {}
			createnode(treedic,treeroot)
			for i in range(len(namelist)-1):
				createnode(treedic,namelist[i+1])
				addedge(treedic, namelist[i], namelist[i+1])
				nodeorder[0:0] = [namelist[i+1]]
			return (treeroot, nodeorder, nodehidden, nodeleaf, treedic)			
			
		def mst(weightmatrix,weightmatrixindex):
			import math
		
			treedic = {}
			nodelist = list(weightmatrixindex)
			nodelisttemp = array(list(nodelist))
			nodenumber = len(list(weightmatrixindex))
			treeroot = nodelist[0]
			nodelist.remove(treeroot)
		
			nodeaddedindex = (nodelisttemp == treeroot)
			nodeadded = list(array(nodelisttemp)[nodeaddedindex])
			noderemainindex = (nodelisttemp != treeroot)
			noderemain = list(array(nodelisttemp)[noderemainindex])
		
			nodeorder = [treeroot]
			createnode(treedic,treeroot)
			nodeleaf = list(weightmatrixindex)
			while len(nodelist)>0:
		
				weightmatrixtemp1 = weightmatrix[nodeaddedindex,:]
				weightmatrixtemp = weightmatrixtemp1[:,noderemainindex ]
		
				maxindex = weightmatrixtemp.argmax()
		
				maxrowindex = int(math.floor(maxindex /len(noderemain)))
				maxcolindex = int(maxindex % len(noderemain))
				edgefromadded = nodeadded[maxrowindex]
				edgefromremain = noderemain[maxcolindex ]
				createnode(treedic,edgefromremain)
				addedge(treedic,edgefromadded,edgefromremain)
				
				nodeaddedindex[nodelisttemp == edgefromremain] =True
				nodeadded = list(array(nodelisttemp)[nodeaddedindex])
				noderemainindex[nodelisttemp == edgefromremain] = False
				noderemain = list(array(nodelisttemp)[noderemainindex])
				nodeorder[0:0] = [edgefromremain]
				nodelist.remove(edgefromremain)
				if edgefromadded in nodeleaf:
					nodeleaf.remove(edgefromadded)
			return treeroot, nodeorder, nodeleaf, treedic
		
		
		def messagepassingu(treeroot, nodeorder, nodehidden, nodeleaf, treedic, textbyline, linerepeat,namelist ):
			#import operator
			#reduce(operator.mul, (3, 4, 5))
			probsame = 0.95
			
			textbylinearray = array(list(textbyline))
			linenumber = len(textbyline)
			textdiffer = list(set(textbyline[0]))
			if '?' in textdiffer:
				textdiffer.remove('?')
			textdiffer.sort()
			textdiffernumber = len(textdiffer)
			probelement = 1.0/float(textdiffernumber) # prob of a
			probchangearray = identity(textdiffernumber,float)*probsame 
			probchangearray[probchangearray==0]=(1-probsame )/textdiffernumber # prob a->b [aa ab] [ba bb]
			probchangearrayT = probchangearray.T
			# log matrix: log P(a->b(t)) - log P(b)
			logarray = log(probchangearray)-log(ones((textdiffernumber,textdiffernumber))*probelement)
		
		
			smalludic = {}
			bigudic = {}
			probnodedic = {}
			probedgedic = {}
			countdic = {}
			weightdic = {}
			
			#++++++++++++++++++++++++++++++++++++++#
			# big u, small u message
		
			for nodei in nodeorder: # from leaf to root
				if nodei in nodeleaf: # big u for leaf nodes
					for parenti in treedic[nodei]['parent']:
						bigudic[(nodei,parenti)] = zeros( (linenumber,textdiffernumber) )
						if namelist.has_key(nodei): # known nodes
							texti = textbylinearray[:,namelist[nodei]]
							for textdifferi in range(textdiffernumber): # assign for know character
								bigudic[(nodei,parenti)][texti==textdiffer[textdifferi],textdifferi ]=1
							bigudic[(nodei,parenti)][texti=='?',:]=1
						else: # unknown nodes
							bigudic[(nodei,parenti)]=ones( (linenumber,textdiffernumber) )
				else: # big u for internal nodes
					for parenti in treedic[nodei]['parent']:
						if namelist.has_key(nodei): # known nodes
							bigudic[(nodei,parenti)] = zeros( (linenumber,textdiffernumber) )
							texti = textbylinearray[:,namelist[nodei]]
							for textdifferi in range(textdiffernumber): # assign for know character
								bigudic[(nodei,parenti)][texti==textdiffer[textdifferi],textdifferi ]=1
							unknownpositioni = (texti=='?')
							bigudic[(nodei,parenti)][unknownpositioni,:]=1
							for childi in treedic[nodei]['child']:
								bigudic[(nodei,parenti)][unknownpositioni ,:]=bigudic[(nodei,parenti)][unknownpositioni,:]*smalludic[(childi,nodei)][unknownpositioni,:]
						else: # unkonwn nodes
							bigudic[(nodei,parenti)] = ones( (linenumber,textdiffernumber) )
							for childi in treedic[nodei]['child']:
								bigudic[(nodei,parenti)]=bigudic[(nodei,parenti)]*smalludic[(childi,nodei)]
		
				# small u
				for parenti in treedic[nodei]['parent']:
					smalludic [(nodei,parenti)] = dot(bigudic[(nodei,parenti)] , probchangearrayT)
				
			nodeorderreverse = list(nodeorder)
			nodeorderreverse.reverse()
		
			for nodei in nodeorderreverse: # from root to leaf
				if nodei not in nodeleaf: # big u
					if namelist.has_key(nodei):
						texti = textbylinearray[:,namelist[nodei]]
						unknownpositioni = (texti=='?')
						for childi in treedic[nodei]['child']: # pass message to all children
							bigudic[(nodei,childi)] = zeros( (linenumber,textdiffernumber) )
							for textdifferi in range(textdiffernumber): # assign for known character
								bigudic[(nodei,childi)][texti==textdiffer[textdifferi],textdifferi ]=1
							
							neighbori = list(treedic[nodei]['neighbor'])
							neighbori.remove(childi)
							bigudic[(nodei,childi)][unknownpositioni,:]=1
							for neighborii in neighbori:
								bigudic[(nodei,childi)][unknownpositioni ,:]=bigudic[(nodei,childi)][unknownpositioni,:]*smalludic[(neighborii ,nodei)][unknownpositioni,:]
					else: # unknown nodes
						for childi in treedic[nodei]['child']:
							neighbori = list(treedic[nodei]['neighbor'])
							neighbori.remove(childi)
							bigudic[(nodei,childi)]=ones( (linenumber,textdiffernumber) )
							for neighborii in neighbori:
								bigudic[(nodei,childi)]=bigudic[(nodei,childi)]*smalludic[(neighborii ,nodei)]
				# small u
				for childi in treedic[nodei]['child']:
					smalludic [(nodei,childi)] = dot(bigudic[(nodei,childi)] , probchangearrayT)
		
				
			
			#++++++++++++++++++++++++++++++++++++++#
			# prob of characters
			for nodei in nodeorder[0:(-1)]: # from leaf to root
				probnodedic[nodei] = probelement * bigudic[(nodei,treedic[nodei]['parent'][0])] * smalludic[(treedic[nodei]['parent'][0],nodei)]
				normalizingvector = array([probnodedic[nodei] .sum(1)])
				normalizingmat = normalizingvector .repeat([textdiffernumber],axis=0)
				probnodedic[nodei]  = probnodedic[nodei] /(normalizingmat.T)
			
			probnodedic[treeroot] = probelement * bigudic[(treeroot,treedic[treeroot]['child'][0])] * smalludic[(treedic[treeroot]['child'][0],treeroot)]
			normalizingvector = array([probnodedic[treeroot] .sum(1)])
			normalizingmat = normalizingvector .repeat([textdiffernumber],axis=0)
			probnodedic[treeroot]  = probnodedic[treeroot] /(normalizingmat.T)
			
			
			#++++++++++++++++++++++++++++++++++++++#
			# prob of edge of linked nodes
			for nodei in nodeorder[0:(-1)]: # from leaf to root
				for parenti in treedic[nodei]['parent']:
					probedgedic [(nodei,parenti)]=[]
					probedgedic [(parenti,nodei)]=[]
					for linei in range(linenumber):
						proba = probelement
						biguij = bigudic[(nodei,parenti)][linei,:]
						biguji = bigudic[(parenti,nodei)][linei,:]
						probab = probchangearray # [[a->a  a->b][b->a  b->b]]
						
						# s1 =[[a a] [b b]] = p(a) * Uij(a)
						s1 = array([proba * biguij]).T.repeat([textdiffernumber],axis=1)
						
						# s2 = s1 * p(a->b)
						s2 = s1 * probab
						# s3 = s2 * Uji(b)  [[a b][a b]]
						s3 = s2 * (array([biguji]).repeat([textdiffernumber],axis=0))
						s4 = s3/sum(s3)
						probedgedic [(nodei,parenti)].append(s4)
						probedgedic [(parenti,nodei)].append(s4.T)
		
		
			#++++++++++++++++++++++++++++++++++++++#
			# prob count
			nodepooled = [treeroot]
			for nodei in nodeorderreverse[1:]:
				for nodej in nodepooled:
					if nodej in treedic[nodei]['parent']: 
						# first repeat array, then sum
						countdic[(nodei,nodej)] = (array(probedgedic[(nodei,nodej)]).repeat(linerepeat,axis=0)).sum(0)
						# weight = sum (S(a->b) * log array)
						weightdic[(nodei,nodej)] = sum( countdic[(nodei,nodej)] *logarray)
						weightdic[(nodej,nodei)] =weightdic[(nodei,nodej)]
					else:
						parenti = treedic[nodei]['parent'][0]
						probedgedic[(nodei,nodej)] = []
						probedgedic[(nodej,nodei)] = []
						weightdic[(nodei,nodej)] = 0
						for linei in range(linenumber): # sum(Pij(a->b)*Pji(b->c)/P(j=b)) by b
							probmiddle = array([probnodedic[parenti][linei]]).T.repeat(textdiffernumber,axis=1)
							probmiddle [probmiddle==0] = 1
							probunlinkedi = dot( probedgedic[(nodei,parenti)][linei], probedgedic[(parenti,nodej)][linei]/probmiddle)
							
							probedgedic[(nodei,nodej)].append(probunlinkedi)
							probedgedic[(nodej,nodei)].append(probunlinkedi.T)
							
							weightdic[(nodei,nodej)] = weightdic[(nodei,nodej)]+sum(probunlinkedi*logarray*linerepeat[linei])
						weightdic[(nodej,nodei)] = weightdic[(nodei,nodej)]
				#print "%s" % (weightdic[(nodej,nodei)])
				nodepooled.append(nodei)
		
			return (weightdic)
		
		
		def treetodot(treedic,nodeorder,nodehidden,resultfolder,resultfile):
			# how to print dot file 'neato -Tpdf -Gstart=rand x.dot > x.pdf'
			import os
			outstr = 'graph clustering {\n\tsize=\"5,5\"\n\n'
			for node in nodeorder:
				if node in nodehidden:
					outstr = outstr + '\t' + node + ' [shape=point];\n'
				else:
					outstr = outstr + '\t' + node + ' [label=\"'+ node + '\" shape=plaintext fontsize=24];\n'	
			outstr = outstr + '\n'
			
		
			for nodei in nodeorder:
				if len(treedic[nodei]['parent'])>0:
					for nodej in treedic[nodei]['parent']:
						outstr = outstr + '\t' + nodei + ' -- ' + nodej + ';\n'
			outstr = outstr + '}'
			
			#filename = os.path.splitext(resultfile)[0]
			dot_file = os.path.join(resultfolder,resultfile) +'.dot' 
			svg_file = os.path.join(resultfolder,resultfile) +'.svg'
			file = open(dot_file,'w')
			file.write(outstr)
			file.close()
			os.system('neato -Tsvg -Gstart=rand ' + dot_file + ' > ' + svg_file)
			

		def tree2newick(treedic, nodeorder, nodehidden, resultfolder, resultfile):
			nodelist = list(nodeorder)
			outstr = ['(',nodelist[0],')',';']
			
			nodelistnotextended = list(nodelist)
			while len(nodelistnotextended) > 0:
				nodelistnotextendedtemp = list(nodelistnotextended)
				for node in nodelistnotextended:
					if node in outstr:
						nodelistnotextendedtemp.remove(node)
						nodeindex = outstr.index(node)
						temp = ['(']
						for neighbori in treedic[node]['neighbor']:
							if neighbori not in outstr:
								temp.append(neighbori)
								temp.append(',')
								if len(treedic[neighbori]['neighbor'])==1:
									nodelistnotextendedtemp.remove(neighbori)

						if len(temp) > 0:
							if temp[len(temp)-1]==',':
								temp.pop(len(temp)-1)
						temp.append(')')
						outstr[nodeindex:nodeindex] = temp
				nodelistnotextended = list(nodelistnotextendedtemp)

			for node in nodehidden:
				outstr.remove(node)
			outstrtemp = ''
			for outstri in outstr:
				outstrtemp = outstrtemp + outstri
			tre_file = self.newick_path
			with open(tre_file,'w') as f:
				f.write(outstrtemp)


		def semuniform (inputfile, iterationmax):

			# step 1 read file
			namelist ,datadic, textdata = readfile(inputfile)
			# step 2 initiation by nj tree
			#treeroot, nodeorder, nodehidden, nodeleaf, treedic = njtree (textdata)
			treeroot, nodeorder, nodehidden, nodeleaf, treedic = nohiddeninitial(textdata)
			# step 3 calculate weight matrix
			logstr = 'Start at'+ str (time.gmtime()) + '\n'
			sigma = 0
			qscoreold = float(-Inf)
			bestiteration = -1
			treedicold = treedic
			nodeorderold = nodeorder
			logvector = [['iteration'],['sigma'],['qscore']]
			resfolder = self.run_args['outfolder']
			resfoldertree = os.path.join(resfolder,'tree')
			if not os.path.exists(resfolder):
				os.makedirs(resfolder)
			if not os.path.exists(resfoldertree):
				os.makedirs(resfoldertree)
		
			for iteration in range(iterationmax):
				print iteration
				#print (time.gmtime())
		#		if (iteration % 100) ==0:
		#			print (iteration)
				weightmatrix = zeros((len(nodeorder),len(nodeorder)))
				weightmatrixwithnoise = zeros((len(nodeorder),len(nodeorder)))
				weightmatrixindex = list(nodeorder)
				for datadickey in datadic.keys():
		
					textbylinewithrepeat = datadic[datadickey]
					linerepeat = []
					textbyline = []
					for textbylinewithrepeati in textbylinewithrepeat:
						if textbylinewithrepeati not in textbyline:
							textbyline.append(textbylinewithrepeati)
							linerepeat.append(1.0)
						else:
							lineindex = textbyline.index(textbylinewithrepeati)
							linerepeat[lineindex]= linerepeat[lineindex]+1.0
		
					weightdic = messagepassingu(treeroot, nodeorder, nodehidden, nodeleaf, treedic, textbyline, linerepeat,namelist )
					for ni in range(0,(len(nodeorder)-1)):
						for nj in range((ni+1),len(nodeorder)):
							weightmatrix[ni,nj] = weightmatrix[ni,nj] +weightdic[(nodeorder[ni],nodeorder[nj])]
							weightmatrix[nj,ni] = weightmatrix[ni,nj]
		
		
		
				for ni in range(len(nodeorder)):
					for nj in range(len(nodeorder)):
						if ni != nj:
							weightmatrixwithnoise[ni,nj] = weightmatrix[ni,nj] + random.gauss(0, sigma)
							weightmatrixwithnoise[nj,ni] = weightmatrixwithnoise[ni,nj]	
						else:
							weightmatrixwithnoise[ni,ni] = float('Inf')
				treeroot, nodeorder, nodeleaf, treedic= mst(weightmatrixwithnoise,weightmatrixindex)
				
				qscore = 0.0
				for nodei in nodeorder[0:(-1)]:
					qscore = qscore + weightmatrix[weightmatrixindex.index(nodei),weightmatrixindex.index(treedic[nodei]['parent'][0])]
		
		
				
				logvector[0].append(iteration)
				logvector[1].append(sigma)
				logvector[2].append(qscore)
			
				if iteration > 10:
					if (abs(logvector[2][-2] - logvector[2][-3]) < 0.001) and (abs(logvector[2][-1] - logvector[2][-2])< 0.001):
						#print ('stop at' + str(iteration) + '\n')						
						break	
		
				print "Scores current: %s old: %s" % (qscore, qscoreold)
				if qscore > qscoreold:
					treedicold = treedic
					nodeorderold = nodeorder
					qscoreold = qscore
					bestiteration = iteration
		
				treedicremoved,nodehiddenremoved = removehidden(nodehidden,treedic)
				treetodot(treedicremoved,treedicremoved.keys(),nodehiddenremoved, resfoldertree, str(iteration).zfill(4))
		
				if iteration >= 2:
					sigma = float(sigma0)*((1.0-float(iteration)/float(iterationmax))**2.0)
				elif iteration == 1:
					sigma0 = 1.0* max(abs(weightmatrix.min()),abs(weightmatrix.max()))
					sigma = sigma0
		
			treediclast,nodehiddenlast =  removehidden(nodehidden,treedic)
			tree2newick(treediclast ,treediclast.keys(),nodehiddenlast, resfoldertree,'treelast')
			
		
			treedicbest,nodehiddenbest = removehidden(nodehidden,treedicold)
			tree2newick(treedicbest ,treedicbest.keys(),nodehiddenbest, resfoldertree,'treebest')
			utils.tree2img(self.newick_path, self.image_path, self.run_args['learnlength'], radial = False)
			
			logstr = logstr + 'End at'+ str (time.gmtime()) + '\n' + 'best iteration is ' + str(bestiteration) +'\n' + 'best qscore is ' + str(qscoreold) + '\n\n\n'
			inumber = len(logvector)
			jnumber = len(logvector[0])
			for j in range(jnumber):
				for i in range(inumber):
					logstr = logstr + str(logvector[i][j]) + '\t'
				logstr = logstr.strip() + '\n'
			logstr = logstr.strip()
			
			file = open(os.path.join(resfolder,'log'),'w')
			file.write(logstr)
			file.close()
			return (qscoreold, bestiteration)
		
		qscore, bestiteration = semuniform(self.run_args['infile'], self.run_args['itermaxin'])
		print "best iteration was: %d" % bestiteration
		self._put_in_results_({'qscore': qscore})
		self._stop.value = 1
		

