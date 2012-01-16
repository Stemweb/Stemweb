#### load function
source('runsemf81.r') # for calculating the tree using f81 model

#print(commandArgs())


##### 1 f81 model ####
runsemf81(infile=inf, outfolder=of, runmax=rm, itermaxin=im, approximationin=a)
