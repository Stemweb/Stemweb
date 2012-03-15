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
from rpy2 import *



def treetonet(treedic):
	nodelist = list(treedic.rx2('NodeList'))
	parentlist = treedic.rx2('ParentList')
	parentlistname = parentlist.names
	outstr = ''
	for node in nodelist:
		if node in parentlistname:
			neighbor = list(parentlist.rx2(node))

			for neighbori in neighbor:
				outstr = outstr + node + '\t' + neighbori + '\n'

	outstr = outstr.strip()
	return (outstr)



		
#####################################################################
def treetomatrix(treedic):
	neighborlist = treedic.rx2('NeighbourList')
	nodelist = list(treedic.rx2('NodeList'))

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
			elif nodej in neighborlist.rx2(nodei):
				outstrtmp = outstrtmp + ' ' + '1'
			else:
				outstrtmp = outstrtmp + ' ' + '-1'					
		outstrtmp = outstrtmp.strip()
		outstr = outstr + '\n' + outstrtmp		
	return (outstr)

###################################################################
def treetodot(treedic):
	# how to print dot file 'neato -Tpdf -Gstart=rand x.dot > x.pdf'
	import re
	nodelist = list(treedic.rx2('NodeList'))

	parentlist = treedic.rx2('ParentList')
	parentlistname = parentlist.names
	outstr = 'graph clustering {\n\tsize=\"5,5\"\n\n'

	for node in nodelist:
		if len(re.findall(r'[a-zA-Z]',node)) == 0:
			outstr = outstr + '\t' + node + ' [shape=point];\n'
		else:
			outstr = outstr + '\t' + node + ' [label=\"'+ node + '\" shape=plaintext fontsize=24];\n'	
	outstr = outstr + '\n'

	for node in nodelist:
		if node in 	parentlistname:
			neighbor = list(parentlist.rx2(node))
			for neighbori in neighbor:
				outstr = outstr + '\t' + node + ' -- ' + neighbori + ';\n'

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
	outstr = 'The run_script stop at iteration: ' + str(iternow) + '\n'
	outstr = outstr + 'There are ' + str(runmax) + ' runs at the same time\n'
	outstr = outstr + 'The average time for each iteration is ' + str(itertimeaverage) + ' seconds \n'
	outstr = outstr + 'The best tree is generation by run_script ' + str(bestruntmp[0]) + ' with qscore ' + str(bestqscore[0]) + '\n'
	outstr = outstr + 'The best tree in the last iteration is generation by run_script ' + str(bestlastruntmp[0]) + ' with qscore ' + str(bestlastqscore) + '\n\n'
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



def writefile(iterationrunres,itertime, bestruntmp,bestlastruntmp,iternow,outfolder):
	import os

	#iterationrunres = Rres.rx2('iterationrunres')
	#itertime = Rres.rx2('itertime')
	#bestruntmp = Rres.rx2('bestruntmp')
	#bestlastruntmp = Rres.rx2('bestlastruntmp')
	#iternow = Rres.rx2('iter')
	
	
	# pull out the values that are needed
	temp = iterationrunres.rx2('bestres')
	bestres = temp.rx2(bestruntmp[0])
	besttree = bestres.rx2('MTreef81res')

	temp = iterationrunres.rx2('runres')
	bestlastres = temp.rx2(bestlastruntmp[0])
	bestlasttree = bestlastres.rx2('MTreef81res')

	# save results
	# net file
	outfolder = outfolder.strip('/')
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
		os.system('chmod 777 ' + outfolder)

	def writestr(outfolder, filename, outstr):
		f = open(outfolder+filename,'w')
		f.write(outstr)
		f.close()		

	# net file
	bestnet = treetonet(treedic=besttree)
	bestlastnet = treetonet(treedic=bestlasttree)
	writestr(outfolder,'/besttree.net',bestnet)
	writestr(outfolder,'/bestlasttree.net',bestlastnet)


	# matrix file
	bestmatrix = treetomatrix(treedic=besttree)
	bestlastmatrix = treetomatrix(treedic=bestlasttree)
	writestr(outfolder,'/besttree.matrix',bestmatrix)
	writestr(outfolder,'/bestlasttree.matrix',bestlastmatrix)

	# dot file
	bestdot = treetodot(treedic=besttree)
	bestlastdot = treetodot(treedic=bestlasttree)
	writestr(outfolder,'/besttree.dot',bestdot)
	writestr(outfolder,'/bestlasttree.dot',bestlastdot)

	# log file
	logstr = writelog(iternow=iternow, itertime=itertime, iterationrunres=iterationrunres, bestruntmp=bestruntmp, bestlastruntmp=bestlastruntmp)
	writestr(outfolder,'/log',logstr)
	# plot dot file to png

	os.system('chmod 777 ' + outfolder+'/besttree.dot')
	os.system('chmod 777 ' + outfolder+'/bestlasttree.dot')
	os.system('neato -Tpng -Gstart=rand ' + outfolder + '/besttree.dot > ' + outfolder+ '/besttree.png')
	os.system('neato -Tpng -Gstart=rand ' + outfolder + '/bestlasttree.dot > ' + outfolder+ '/bestlasttree.png')


	# close permissions
	os.system('chmod 755 ' + outfolder+'/besttree.dot')
	os.system('chmod 755 ' + outfolder+'/bestlasttree.dot')
	os.system('chmod 755 ' + outfolder)

def writefile(iterationrunres,itertime, bestruntmp,bestlastruntmp,iternow,outfolder):
	import os

	#iterationrunres = Rres.rx2('iterationrunres')
	#itertime = Rres.rx2('itertime')
	#bestruntmp = Rres.rx2('bestruntmp')
	#bestlastruntmp = Rres.rx2('bestlastruntmp')
	#iternow = Rres.rx2('iter')
	
	
	# pull out the values that are needed
	temp = iterationrunres.rx2('bestres')
	bestres = temp.rx2(bestruntmp[0])
	besttree = bestres.rx2('MTreef81res')

	temp = iterationrunres.rx2('runres')
	bestlastres = temp.rx2(bestlastruntmp[0])
	bestlasttree = bestlastres.rx2('MTreef81res')

	# save results
	# net file
	outfolder = outfolder.strip('/')
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
		os.system('chmod 777 ' + outfolder)

	def writestr(outfolder, filename, outstr):
		f = open(outfolder+filename,'w')
		f.write(outstr)
		f.close()		

	# net file
	bestnet = treetonet(treedic=besttree)
	bestlastnet = treetonet(treedic=bestlasttree)
	writestr(outfolder,'/besttree.net',bestnet)
	writestr(outfolder,'/bestlasttree.net',bestlastnet)


	# matrix file
	bestmatrix = treetomatrix(treedic=besttree)
	bestlastmatrix = treetomatrix(treedic=bestlasttree)
	writestr(outfolder,'/besttree.matrix',bestmatrix)
	writestr(outfolder,'/bestlasttree.matrix',bestlastmatrix)

	# dot file
	bestdot = treetodot(treedic=besttree)
	bestlastdot = treetodot(treedic=bestlasttree)
	writestr(outfolder,'/besttree.dot',bestdot)
	writestr(outfolder,'/bestlasttree.dot',bestlastdot)

	# log file
	logstr = writelog(iternow=iternow, itertime=itertime, iterationrunres=iterationrunres, bestruntmp=bestruntmp, bestlastruntmp=bestlastruntmp)
	writestr(outfolder,'/log',logstr)
	# plot dot file to png

	os.system('chmod 777 ' + outfolder+'/besttree.dot')
	os.system('chmod 777 ' + outfolder+'/bestlasttree.dot')
	os.system('neato -Tpng -Gstart=rand ' + outfolder + '/besttree.dot > ' + outfolder+ '/besttree.png')
	os.system('neato -Tpng -Gstart=rand ' + outfolder + '/bestlasttree.dot > ' + outfolder+ '/bestlasttree.png')


	# close permissions
	os.system('chmod 755 ' + outfolder+'/besttree.dot')
	os.system('chmod 755 ' + outfolder+'/bestlasttree.dot')
	os.system('chmod 755 ' + outfolder)

def writefilelite(iterationrunres,itertime, bestruntmp,iternow,outfolder):
	import os

	temp = iterationrunres.rx2('bestres')
	bestres = temp.rx2(bestruntmp[0])
	besttree = bestres.rx2('MTreef81res')
	

	outfolder = outfolder.strip('/')
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
		os.system('chmod 777 ' + outfolder)
		
	def writestr(outfolder, filename, outstr):
		f = open(outfolder+filename,'w')
		f.write(outstr)
		f.close()		

	bestdot = treetodot(treedic=besttree)
	writestr(outfolder,'/besttree.dot',bestdot)

	os.system('chmod 777 ' + outfolder+'/besttree.dot')
	os.system('neato -Tpng -Gstart=rand ' + outfolder + '/besttree.dot > ' + outfolder+ '/besttree.png')			
	os.system('chmod 755 ' + outfolder+'/besttree.dot')
	os.system('chmod 755 ' + outfolder)
			
			
			
			
			
			
			
			
			
			
			
			