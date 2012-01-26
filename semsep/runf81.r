
runf81 <- function(filein, runmax, itermax, approximation)
{
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
		iter = iter,
		converge = iterationrunres[["converge"]])
		if (iter < 10)
		{
			itertime = c(itertime, iterationrunres[["itertime"]])
		}
	}


	#_________________________________________________________________________
	# 3 start from the best result onw

	# Assign starting value
	bestruntmp <- findbestrun(iterationrunres=iterationrunres, runmax=runmax)	
	iterationrunres <- updateres(runmax=runmax, bestruntmp=bestruntmp, iterationrunres=iterationrunres)

	# start from iter+1
	itertmp = iter+1
	for (iter in c(itertmp:itermax))
	{
		iterationrunres <- iterationrun(runmax=runmax, approximation=approximation, 
		runres = iterationrunres[["runres"]], 
		bestres = iterationrunres[["bestres"]],
		iter = iter,
		converge = iterationrunres[["converge"]])	
		if (sum(iterationrunres[["converge"]])==length(iterationrunres[["converge"]]))
		{
			break # if two runs are coverged, break and return
		}		
	}
	# find the best result id when return
	bestruntmp <- findbestrun(iterationrunres=iterationrunres, runmax=runmax)
	bestlastruntmp <- findbestlastrun(iterationrunres=iterationrunres, runmax=runmax)

	runf81res = list("iterationrunres"=iterationrunres, "bestruntmp"=bestruntmp,
	"bestlastruntmp"=bestlastruntmp, "iter"=iter, 'itertime'=itertime)
	
	invisible (runf81res)
}



runf81res = runf81(filein = "test.nex", itermax = 20, runmax = 2, approximation = 0)