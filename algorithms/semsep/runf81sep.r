filein = "test.nex"
folderout = "semres"
runmax = 2
itermax = 20
approximation = 0



##########################################################################




#_________________________________________________________________________
# 1 initiation
initiationrunres <- initiationrun(runmax=runmax, itermax=itermax,
filein=filein, approximation=approximation)

#_________________________________________________________________________
# 2 The first stages for all runs
iterationrunres = initiationrunres
itertime = NULL
for (iter in c(2:(ceiling(itermax*0.1)+1)))
{
	iterationrunres <- iterationrun(runmax=runmax, approximation=approximation, 
	runres = iterationrunres[["runres"]], 
	bestres = iterationrunres[["bestres"]],
	iter=iter)
	if (iter < 10)
	{
		itertime = c(itertime, iterationrunres[["itertime"]])
	}
}


#_________________________________________________________________________
# 3 start from the best result onw

# Assign starting value
bestruntmp <- findbestrun(iterationrunres=iterationrunres, runmax=runmax)
bestrestmp = iterationrunres[["bestres"]]
iterationrunres <- updateres(runmax=runmax, bestruntmp=bestruntmp, iterationrunres=iterationrunres)

# start from iter+1
itertmp = iter+1
for (iter in c(itertmp:itermax))
{
	iterationrunres <- iterationrun(runmax=runmax, approximation=approximation, 
	runres = iterationrunres[["runres"]], 
	bestres = iterationrunres[["bestres"]],
	iter=iter)
}

bestruntmp <- findbestrun(iterationrunres=iterationrunres, runmax=runmax)
bestlastruntmp <- findbestlastrun(iterationrunres=iterationrunres, runmax=runmax)





