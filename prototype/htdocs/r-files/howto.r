#### load function
source('./../htdocs/r-files/runsemf81.r') # for calculating the tree using f81 model
#source('runsemmdl.r') # for calculating the tree using mdl model
#source('runsemuni.r') # for calculating the tree using uniform model

args=(commandArgs(TRUE))
if(length(args)==0) print("Booohoooo")

print(commandArgs())

##### 1 f81 model ####
runsemf81(infile='./../htdocs/r-files/test.nex', outfolder='./../htdocs/out', 
runmax=2, itermaxin=5,
approximationin=0)
# infile: the full path of your file in nexus format
# out folder: the folder containing the results
# runmax: the maximum number of simultaneous runs
# approximationin: =1 if want approximation when calculating weight matrix, 0 for not using approximation


##### 2 mdl model ###
#runsemmdl(infile='/media/F/work/semori/semdata/par.nex', infilecsv='/media/F/work/semori/semdata/par.csv',outfolder='/media/F/work/semori/semres', 
#runmax=2, itermaxin=20,
#approximationin=0)
# infilecsv: the aligned table of text files, separated by tab
# others the same as f81 model


###### 3 uniform model ###
#runsemuni(infile='/media/F/work/semori/semdata/test.nex', outfolder='/media/F/work/semori/semres', 
#runmax=2, itermaxin=20,
#ProbSamein=0.95, approximationin=0)
# ProbSamein: the probability defined for the probability of a word staying unchanged 



