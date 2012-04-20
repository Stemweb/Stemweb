#!/usr/bin/env python


# The python scripts will return the string for print out in files
# It does not creating files
# It use the results from R program

# The parameters it gets from R program include:
# 'iterationrunres' : the result when iteration stops
# 'itertime' : a vector store time for each iteration, for caculating average time per iter
# 'bestruntmp': the run_script id with the best result when stop
# 'bestlastruntmp': the run_script id with the best last result when stop
# 'iter': The iteration id when stopping

# treetonet(treedic): generate string for net file
# treetomatrix(treedic): generate string for matrix file
# treetodot(treedic): generate string for dot file (for plotting pdf)
# writelog(iternow, itertime, iterationrunres, bestruntmp, bestlastruntmp): 
# generate string for log file


# _______________the useful functions______________________________________________

######################################################################
from rpy2 import robjects
import os
import unicodedata
import logging

#def treetonet(nodelist,parentlist,treedic,lenmat):
def treetonet(nodelist,parentlist,lenmat):
	parentlistname = parentlist.keys()
	outstr = ''
	if type(lenmat)==str:
		for node in nodelist:
			if node in parentlistname:
				neighbor = parentlist[node]
				for neighbori in neighbor:
					outstr = outstr + node + '\t' + neighbori + '\n'
		outstr = outstr.strip()
	else:
		for node in nodelist:
			if node in parentlistname:
				neighbor = parentlist[node]
				for neighbori in neighbor:
					outstr = outstr + node + '\t' + neighbori + '\t' + str(lenmat[(node,neighbori)]) + '\n'
		outstr = outstr.strip()
	return (outstr)


def treetonewick(nodelist,neighborlist,lenmat):
	import re
	for node in neighborlist.keys():
		if len(neighborlist[node])>1:
			break
	outstr = [node,';']
	
	nodelistnotextended = list(nodelist)
	while len(nodelistnotextended) > 0:
		nodelistnotextendedtemp = list(nodelistnotextended)
		for node in nodelistnotextended:
			if (node in outstr) and (node in nodelistnotextendedtemp):

				nodelistnotextendedtemp.remove(node)
				nodeindex = outstr.index(node)
				temp = []
				for neighbori in neighborlist[node]:
					if neighbori not in outstr:
						temp.append(neighbori)
						if type(lenmat) != str:
							temp.append(':')
							temp.append(str(lenmat[(node,neighbori)]))
						temp.append(',')
						if len(neighborlist[neighbori])==1:
							nodelistnotextendedtemp.remove(neighbori)
					
				if len(temp) > 0:
					if temp[len(temp)-1]==',':
						temp.pop(len(temp)-1)
					temp[0:0]=['(']
					temp.append(')')
				outstr[nodeindex:nodeindex] = temp
		nodelistnotextended = list(nodelistnotextendedtemp)
	for node in nodelist:
		if len(re.findall(r'[a-zA-Z]',node))==0:
			outstr.remove(node)
	outstrtemp = ''
	for outstri in outstr:
		outstrtemp = outstrtemp + outstri
	return (outstrtemp)

	
	
#####################################################################
#def treetomatrix(treedic):
def treetomatrix(neighborlist,nodelist):

	#neighborlist = treedic.rx2('NeighbourList')
	#nodelist = list(treedic.rx2('NodeList'))

	nodenumber = len(nodelist)
	nodelist.sort()
	outstr = str(nodenumber)
	for nodei in nodelist:
		outstr = outstr + '\n' + nodei
	for nodei in nodelist:
		outstrtmp = ''
		for nodej in nodelist:
			if nodei == nodej:
				outstrtmp = outstrtmp + ' ' + '0'
			elif nodej in neighborlist[nodei]:
				outstrtmp = outstrtmp + ' ' + '1'
			else:
				outstrtmp = outstrtmp + ' ' + '-1'					
		outstrtmp = outstrtmp.strip()
		outstr = outstr + '\n' + outstrtmp		
	return (outstr)

###################################################################
def treetodot(nodelist,parentlist,lenmat):
	# how to print dot file 'neato -Tpdf -Gstart=rand x.dot > x.pdf'
	import re
	parentlistname = parentlist.keys()
	outstr = 'graph clustering {\n\tsize=\"5,5\"\n\n'
	for node in nodelist:
		if len(re.findall(r'[a-zA-Z]',node)) == 0:
			outstr = outstr + '\t' + node + ' [shape=point];\n'
		else:
			outstr = outstr + '\t' + node + ' [label=\"'+ node + '\" shape=plaintext fontsize=24];\n'	
	outstr = outstr + '\n'
	
	if type(lenmat)==str:
		for node in nodelist:
			if node in 	parentlistname:
				neighbor = list(parentlist[node])
				for neighbori in neighbor:
					outstr = outstr + '\t' + node + ' -- ' + neighbori + ';\n'
	else:
		lenmax = 0
		lenmin = float('Inf')
		for node in nodelist:
			if node in 	parentlistname:
				neighbor = list(parentlist[node])
				for neighbori in neighbor:
					if lenmax < lenmat[(node,neighbori)]:
						lenmax = lenmat[(node,neighbori)]
					if lenmin > lenmat[(node,neighbori)]:
						lenmin = lenmat[(node,neighbori)]
		outstr = outstr + '\n/* Here are the normalized edge lengths for printing */\n'

		for node in nodelist:
			if node in 	parentlistname:
				neighbor = list(parentlist[node])
				for neighbori in neighbor:
					temp = lenmat[(node,neighbori)]
					temp = (0.6*(temp - lenmin))/(lenmax - lenmin) + 0.4
					outstr = outstr + '\t' + node + ' -- ' + neighbori +'[len=' + str(temp)+ '];\n'
		outstr = outstr + '\n/* Here are the original edge lengths */\n'
		for node in nodelist:
			if node in 	parentlistname:
				neighbor = list(parentlist[node])
				for neighbori in neighbor:
					temp = lenmat[(node,neighbori)]
					outstr = outstr + '/*\t' + node + ' -- ' + neighbori +'[len=' + str(temp)+ '];*/\n'
	outstr = outstr + '}'
	return (outstr)


def writelog(iternow, itertime, iterationrunres, bestruntmp, bestlastruntmp):
	# use append to existing log files
	# the iteration when stopping
	# run_script number
	# average time for one iteration
	# qscore for each run_script
	# best tree & qscore for each run_script
	# last tree & qscore for each run_script
	# best tree & qscore
	# last tree & qscore
	#... indexing ???
	runmax = len(iterationrunres.rx2('runres'))
	itertimeaverage = sum(itertime)/len(itertime)
	temp = iterationrunres.rx2('bestres')
	temp = temp.rx2(bestruntmp[0])
	bestqscore = temp.rx2('qscore')

	temp = iterationrunres.rx2('runres')
	temp = temp.rx2(bestlastruntmp[0])
	temp = temp.rx2('qscorevector')
	bestlastqscore = temp[len(temp)-1]
	outstr = 'The run stop at iteration: ' + str(iternow) + '\n'
	outstr = outstr + 'There are ' + str(runmax) + ' runs at the same time\n'
	outstr = outstr + 'The average time for each iteration is ' + str(itertimeaverage) + ' seconds \n'
	outstr = outstr + 'The best tree is generation by run ' + str(bestruntmp[0]) + ' with qscore ' + str(bestqscore[0]) + '\n'
	outstr = outstr + 'The best tree in the last iteration is generation by run ' + str(bestlastruntmp[0]) + ' with qscore ' + str(bestlastqscore) + '\n\n'
	for run_script in range(runmax):
		outstr = outstr + '****** Here is the information for run_script '+str(run_script+1) + '******\n'
		temp = iterationrunres.rx2('bestres')
		temp = temp.rx2(run_script+1)
		temp = temp.rx2('qscore')
		outstr = outstr + 'The best qscore of ' + str(run_script+1) + ' is ' + str(temp[0]) + '\n'
		temp = iterationrunres.rx2('runres')
		temp = temp.rx2(run_script+1)
		temp = temp.rx2('qscorevector')
		outstr = outstr + 'The last qscore of ' + str(run_script+1) + ' is ' + str(temp[len(temp)-1]) + '\n'
		outstr = outstr + 'The qscore of each iteration is:\n'
		for tempi in temp: 
			outstr = outstr + str(tempi) + ' '
		outstr = outstr + '\n\n'
	return (outstr)



def writestr(outfolder, filename, outstr):
	file_path = os.path.join(outfolder, filename)
	
	try: 
		f = open(file_path,'w')
		os.chmod(file_path, 0777)
		f.write(outstr)
		f.close()
		os.chmod(file_path, 0644)
	except:
		f = open(os.path.join(outfolder, 'saveres_log'), 'a')
		f.write('Could not write into file: %s \n' % (file_path))
		f.close()
		pass
	

def dot2png(outfolder, filename):
	file_path = os.path.join(outfolder, filename)
	os.chmod(file_path, 0777)
	png_name = os.path.splitext(filename)[0] + '.png'	# Change .dot to .png				
	png_path = os.path.join(outfolder, png_name)
	os.system('neato -Tpng -Gstart=rand ' + file_path + '> ' + png_path)
	os.chmod(file_path, 0644)
	os.chmod(png_path, 0644)
	
def dot2svg(outfolder, filename):
	file_path = os.path.join(outfolder, filename)
	os.chmod(file_path, 0777)
	svg_name = os.path.splitext(filename)[0] + '.svg'	# Change .dot to .svg				
	svg_path = os.path.join(outfolder, svg_name)
	os.system('neato -Tsvg -Gstart=rand ' + file_path + '> ' + svg_path)
	os.chmod(file_path, 0644)
	os.chmod(svg_path, 0644)


def writefile(result):
	import re
	iterationrunres = robjects.Vector(result['iterationrunres'])
	itertime = result['itertime']
	bestruntmp = result['bestruntmp']
	bestlastruntmp = result['bestlastruntmp']
	iternow = result['iteri']
	outfolder = result['outfolder']
	
	# pull out the values that are needed
	temp = iterationrunres.rx2('bestres')
	bestres = temp.rx2(bestruntmp[0])
	besttree = bestres.rx2('MTreeunires')


	temp = iterationrunres.rx2('runres')
	bestlastres = temp.rx2(bestlastruntmp[0])
	bestlasttree = bestlastres.rx2('MTreeunires')


	# save results
	# net file
	#outfolder = outfolder.strip('/')
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
		#os.system('chmod 777 ' + outfolder)


	def removehidden(nodelist,parentlist,neighborlist,lenmat):
		nodelistremovetemp = list(nodelist)
		parentlistremovetemp = {}
		neighborlistremovetemp = {}
		lenmatremovetemp = {}
		parentlistname = parentlist.names
		neighborlistname = neighborlist.names
		lenmatremovetemp = {}
		for node in nodelist:
			if node in parentlistname:
				parentlistremovetemp[node] = list(parentlist.rx2(node))
		for node in nodelist:
			if node in neighborlistname:
				neighborlistremovetemp[node] = list(neighborlist.rx2(node))
		if type(lenmat)!=str:
			for nodei in nodelist:
				for nodej in nodelist:
					lenmatremovetemp[(nodei,nodej)]=list(lenmat.rx(nodei,nodej))[0]
					lenmatremovetemp[(nodej,nodei)]=lenmatremovetemp[(nodei,nodej)]
		else:
			lenmatremovetemp = 'nolength'

		
				
		scanfinish = 0
		while scanfinish == 0:
			scanfinish = 1
			
			for node in nodelist:
				if (node in nodelistremovetemp):
					if (len(neighborlistremovetemp[node])==1 and len(re.findall(r'[a-zA-Z]',node)) == 0): 
						# hidden node in the leaf position
						scanfinish = 0
						# remove node from nodelist
						nodelistremovetemp.remove(node)
						# remove node form neighor information
						neighbortemp = neighborlistremovetemp[node][0]
						neighborlistremovetemp[neighbortemp].remove(node)
						if parentlistremovetemp.has_key(neighbortemp):
							if node in parentlistremovetemp[neighbortemp]:
								parentlistremovetemp[neighbortemp].remove(node)
								if len(parentlistremovetemp[neighbortemp])==0:
									del parentlistremovetemp[neighbortemp]
						# remove from neighborlist and parentlist
						if parentlistremovetemp.has_key(node):
							del parentlistremovetemp[node]
						if neighborlistremovetemp.has_key(node):
							del neighborlistremovetemp[node]
						
				if (node in nodelistremovetemp):
					if (len(neighborlistremovetemp[node])==2 and len(re.findall(r'[a-zA-Z]',node))==0): 
						# remove internal hidden nodes only when there is no edge length
						neighborlisttemp = neighborlistremovetemp[node]
						scanfinish = 0
						# change edge length
						if type(lenmatremovetemp)!=str:
							lenmatremovetemp[(neighborlisttemp[1],neighborlisttemp[0])] = lenmatremovetemp[(neighborlisttemp[1],node)] +lenmatremovetemp[(neighborlisttemp[0],node)]
							lenmatremovetemp[(neighborlisttemp[1],neighborlisttemp[0])] = lenmatremovetemp[(neighborlisttemp[0],neighborlisttemp[1])]
						# do something for neighbor 1
						if parentlistremovetemp.has_key(neighborlisttemp[0]):
							if node in parentlistremovetemp[neighborlisttemp[0]]:
								parentlistremovetemp[neighborlisttemp[0]].remove(node)
								parentlistremovetemp[neighborlisttemp[0]].append(neighborlisttemp[1])
						neighborlistremovetemp[neighborlisttemp[0]].remove(node)
						neighborlistremovetemp[neighborlisttemp[0]].append(neighborlisttemp[1])
						# do something for neighbor 2
						if parentlistremovetemp.has_key(neighborlisttemp[1]):
							if node in parentlistremovetemp[neighborlisttemp[1]]:
								parentlistremovetemp[neighborlisttemp[1]].remove(node)
								if parentlistremovetemp.has_key(neighborlisttemp[0]):
									if neighborlisttemp[1] not in parentlistremovetemp[neighborlisttemp[0]]:
										parentlistremovetemp[neighborlisttemp[1]].append(neighborlisttemp[0])
								else:
									parentlistremovetemp[neighborlisttemp[1]].append(neighborlisttemp[0])
								if len(parentlistremovetemp[neighborlisttemp[1]])==0:
									del parentlistremovetemp[neighborlisttemp[1]]
									
						neighborlistremovetemp[neighborlisttemp[1]].remove(node)
						neighborlistremovetemp[neighborlisttemp[1]].append(neighborlisttemp[0])	
						# remove node
						nodelistremovetemp.remove(node)
						if parentlistremovetemp.has_key(node):
							del parentlistremovetemp[node]
						if neighborlistremovetemp.has_key(node):
							del neighborlistremovetemp[node]
						

		return nodelistremovetemp,parentlistremovetemp,neighborlistremovetemp, lenmatremovetemp
		
		
		
		
		
	nodelistbestori=list(besttree.rx2('NodeList'))	
	parentlistbestori=besttree.rx2('ParentList')
	neighborlistbestori=besttree.rx2('NeighbourList')
	nodelistlastori=list(bestlasttree.rx2('NodeList'))	
	parentlistlastori =bestlasttree.rx2('ParentList')	
	neighborlistlastori=bestlasttree.rx2('NeighbourList')
	if ('lenmat' in bestres.names):
		lenmatbestori = bestres.rx2('lenmat')
	else:
		lenmatbestori = 'nolength'
	if ('lenmat' in bestlastres.names):
		lenmatlastori = bestlastres.rx2('lenmat')
	else:
		lenmatlastori = 'nolength'
	nodelistbest, parentlistbest,neighborlistbest, lenmatbest =  removehidden(nodelist=nodelistbestori,parentlist=parentlistbestori,neighborlist=neighborlistbestori, lenmat = lenmatbestori)
	nodelistlast, parentlistlast,neighborlistlast,lenmatlast =  removehidden(nodelist=nodelistlastori,parentlist=parentlistlastori,neighborlist=neighborlistlastori, lenmat = lenmatlastori)
	#print ('hidden removed')
	# net file

	bestnet = treetonet(nodelist=nodelistbest,parentlist =parentlistbest,lenmat=lenmatbest)
	writestr(outfolder,'besttree.net',bestnet)
	bestlastnet = treetonet(nodelist=nodelistlast,parentlist =parentlistlast,lenmat=lenmatlast)
	writestr(outfolder,'bestlasttree.net',bestlastnet)
	#print ('net saved')
	
	# newick file
	bestnewick = treetonewick(neighborlist=neighborlistbest,nodelist=nodelistbest,lenmat=lenmatbest)
	#print (bestnewick )
	lastnewick = treetonewick(neighborlist=neighborlistlast,nodelist=nodelistlast,lenmat=lenmatlast)
	#print (lastnewick)
	writestr(outfolder,'besttree.tre',bestnewick)
	writestr(outfolder,'bestlasttree.tre',lastnewick)	
	#print ('newick saved')
	# matrix file
	bestmatrix = treetomatrix(neighborlist=neighborlistbest,nodelist=nodelistbest)
	bestlastmatrix = treetomatrix(neighborlist=neighborlistlast,nodelist=nodelistlast)
	writestr(outfolder,'besttree.matrix',bestmatrix)
	writestr(outfolder,'bestlasttree.matrix',bestlastmatrix)
	#print ('matrix saved')
	# dot file
	bestdot = treetodot(nodelist=nodelistbest,parentlist =parentlistbest,lenmat=lenmatbest)
	bestlastdot = treetodot(nodelist=nodelistlast,parentlist =parentlistlast,lenmat=lenmatlast)
	writestr(outfolder,'besttree.dot',bestdot)
	writestr(outfolder,'bestlasttree.dot',bestlastdot)
	#print ('dot saved')
	# log file
	logstr = writelog(iternow=iternow, itertime=itertime, iterationrunres=iterationrunres, bestruntmp=bestruntmp, bestlastruntmp=bestlastruntmp)
	writestr(outfolder,'log',logstr)


	# plot dot file to svg
	dot2svg(outfolder, 'besttree.dot')
	dot2svg(outfolder, 'bestlasttree.dot')


def writefilelite(result):
	import os
	iterationrunres = robjects.Vector(result['iterationrunres'])	
	itertime = result['itertime']
	bestruntmp = result['bestruntmp']
	iternow = result['iteri']
	outfolder = result['outfolder']
	temp = iterationrunres.rx2('bestres')
	bestres = temp.rx2(bestruntmp[0])
	besttree = bestres.rx2('MTreeunires')
	

	outfolder = outfolder.strip('/')
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
		os.system('chmod 777 ' + outfolder)
		
	def writestr(outfolder, filename, outstr):
		f = open(outfolder+filename,'w')
		f.write(outstr)
		f.close()		

	bestdot = treetodot(nodelist=list(besttree.rx2('NodeList')),parentlist =besttree.rx2('ParentList'),lenmat=lenmat)
	writestr(outfolder,'/besttree.dot',bestdot)

	os.system('chmod 777 ' + outfolder+'/besttree.dot')
	os.system('neato -Tpng -Gstart=rand ' + outfolder + '/besttree.dot > ' + outfolder+ '/besttree.png')			
	os.system('chmod 755 ' + outfolder+'/besttree.dot')
	os.system('chmod 755 ' + outfolder)
			
			
			
			
			
			
			
			
			
			
			
			