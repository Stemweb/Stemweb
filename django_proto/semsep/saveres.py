#!/usr/bin/env python


# The python scripts will return the string for print out in files
# It does not creating files
# It use the results from R program

# The parameters it gets from R program include:
# 'iterationrunres' : the result when iteration stops
# 'itertime' : a vector store time for each iteration, for caculating average time per iter
# 'bestruntmp': the run id with the best result when stop
# 'bestlastruntmp': the run id with the best last result when stop
# 'iter': The iteration id when stopping

# treetonet(treedic): generate string for net file
# treetomatrix(treedic): generate string for matrix file
# treetodot(treedic): generate string for dot file (for plotting pdf)
# writelog(iternow, itertime, iterationrunres, bestruntmp, bestlastruntmp): 
# generate string for log file


# _______________the useful functions______________________________________________

######################################################################

def treetonet(treedic):
	nodelist = treedic['NodeList']
	parentlist = treedic['ParentList']
	outstr = ''
	for node in nodelist:
		if parentlist.has_key(node):
			neighbor = parentlist[node]
			if type(neighbor)==list:
				for neighbori in neighbor:
					outstr = outstr + node + '\t' + neighbori + '\n'
			if type(neighbor)==str:
				outstr = outstr + node + '\t' + neighbor + '\n'
	outstr = outstr.strip()
	return (outstr)



		
#####################################################################
def treetomatrix(treedic):
	neighborlist = treedic['NeighbourList']
	nodelist = treedic['NodeList']

	nodenumber = len(nodelist)
	nodelist.sort(reverse=True)
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
def treetodot(treedic):
	# how to print dot file 'neato -Tpdf -Gstart=rand x.dot > x.pdf'
	import re
	nodelist = treedic['NodeList']
	parentlist = treedic['ParentList']
	outstr = 'graph clustering {\n\tsize=\"5,5\"\n\n'

	for node in nodelist:
		if len(re.findall(r'[a-zA-Z]',node)) == 0:
			outstr = outstr + '\t' + node + ' [shape=point];\n'
		else:
			outstr = outstr + '\t' + node + ' [label=\"'+ node + '\" shape=plaintext fontsize=24];\n'	
	outstr = outstr + '\n'

	for node in nodelist:
		if parentlist.has_key(node):
			neighbor = parentlist[node]
			if type(neighbor)==list:
				for neighbori in neighbor:
					outstr = outstr + '\t' + node + ' -- ' + neighbori + ';\n'
			if type(neighbor)==str:
				outstr = outstr + '\t' + node + ' -- ' + neighbor + ';\n'
	outstr = outstr + '}'
	return (outstr)

def writelog(iternow, itertime, iterationrunres, bestruntmp, bestlastruntmp):
	# use append to existing log files
	# the iteration when stopping
	# run number
	# average time for one iteration
	# qscore for each run
	# best tree & qscore for each run
	# last tree & qscore for each run
	# best tree & qscore
	# last tree & qscore
	runmax = len(iterationrunres['runres'])
	itertimeaverage = sum(itertime)/len(itertime)
	bestqscore = iterationrunres['bestres'][bestruntmp-1]['qscore']
	tmp = iterationrunres["runres"][bestlastruntmp-1]["qscorevector"]
	bestlastqscore = tmp[len(tmp)-1]
	outstr = 'The run stop at iteration: ' + str(iternow) + '\n'
	outstr = outstr + 'There are ' + str(runmax) + 'runs at the same time\n'
	outstr = outstr + 'The average time for each iteration is ' + str(itertimeaverage) + 'seconds \n'
	outstr = outstr + 'The best tree is generation by run ' + str(bestruntmp) + ' with qscore ' + str(bestqscore) + '\n'
	outstr = outstr + 'The best tree in the last iteration is generation by run ' + str(bestlastruntmp) + ' with qscore ' + str(bestlastqscore) + '\n\n'
	for run in range(runmax):
		outstr = outstr + '****** Here is the information for run '+str(run+1) + '******\n'
		outstr = outstr + 'The best qscore of ' + str(run+1) + 'is' + str(iterationrunres['bestres'][run]['qscore']) + '\n'
		tmp = iterationrunres["runres"][run]["qscorevector"]
		outstr = outstr + 'The last qscore of ' + str(run+1) + 'is' + str(tmp[len(tmp)-1]) + '\n'
		outstr = outstr + 'The qscore of each iteration is:\n'
		for tmpi in tmp: 
			outstr = outstr + str(tmpi) + ' '
		outstr = outstr + '\n\n'
	return (outstr)



def writefile(Rres, outfolder):
	import os
	iterationrunres = Rres['iterationrunres']
	itertime = Rres['itertime']
	bestruntmp = Rres['bestruntmp']
	bestlastruntmp = Rres['bestlastruntmp']
	iternow = Rres['iter']
	# pull out the values that are needed
	bestres = iterationrunres['bestres'][bestruntmp-1]
	besttree = bestres['MTreef81res']

	bestlastres = iterationrunres['runres'][bestlastruntmp-1]
	bestlasttree = bestlastres['MTreef81res']

	# save results
	# net file
	outfolder = outfolder.strip('/')
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
		os.system('chmod 777 ' + outfolder)

	def writestr(outfolder, filename, outstr):
		file = open(outfolder+filename,'w')
		file.write(outstr)
		file.close()		

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












