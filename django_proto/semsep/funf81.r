rm(list=ls())

Initialf81 <- function (fileread)
{
	Dataraw = readLines(fileread)
	datastart=1
	for (i in 1:length(Dataraw))
	{
		if (length(grep("matrix",tolower(Dataraw[i])))>0)
		{
			datastart = i+1
			break
		}
	}
	dataend=length(Dataraw)
	for (i in length(Dataraw):1)
	{
		if (length(grep("end",tolower(Dataraw[i])))>0)
		{
			dataend = i-1
			break
		}
	}

	Data=NULL
	for (i in datastart:dataend)
	{
		linetmp=Dataraw[i]
		linetmp=gsub(" ","\t",linetmp)
		linetmp=gsub(";","",linetmp)
		linetmp=unlist(strsplit(linetmp,split="\t"))
		linetmpj=NULL
		for (linetmpi in linetmp)
		{
			if ((length(linetmpi)>0)&(linetmpi!=""))
			{
				linetmpj=c(linetmpj,linetmpi)
			}
		}
		Data=rbind(Data,linetmpj)
	}
	rownames(Data)=NULL	


	TextLen = nchar(toString(Data[1,2]))
	ObservedNodeNumber = dim(Data)[1]
	HiddenNodeNumber = ObservedNodeNumber-2
	AllNodeNumber = ObservedNodeNumber+HiddenNodeNumber

	#1
	PositionDiff = NULL
	PositionProb = list()
	PositionChar = list()
	######################### different from other models ##############	
	for (i in 1:TextLen)
	{ 
		tmp = table(substr(Data[1:ObservedNodeNumber,2],i,i))
		namestmp = names(tmp)
		
		if (sum(namestmp=="?")==1)
		{
		unkowntmp = tmp[namestmp=="?"]
		tmp = tmp[namestmp!="?"] # exclude the unknown character		
		tmp = (tmp+unkowntmp/(length(tmp)))/ObservedNodeNumber
		PositionProb[[i]] = tmp
		PositionChar[[i]] = names(tmp)
	
		}else
		{
		tmp = tmp/ObservedNodeNumber
		PositionProb[[i]] = tmp
		PositionChar[[i]] = namestmp
		}	 
		PositionDiff = c(PositionDiff,length(tmp))
	}
	######################### different from other models ##############
	#3	
	CharList = NULL
	CharListrowname = NULL
	ParentList = list()
	KidList = list()
	NeighbourList = list()
	NodeList = NULL #Root in the last

	for (i in 1:AllNodeNumber)
	{
		if (i<=ObservedNodeNumber)
		{
			tmp = toString(unlist(Data[i,2]))
			CharList = rbind(CharList, substring(tmp, 1:nchar(tmp), 1:nchar(tmp)) )		
			CharListrowname = c(CharListrowname,toString(Data[i,1]))		
		}else
		{
			tmp = rep("?",TextLen)
			CharList = rbind(CharList, tmp)
			CharListrowname = c(CharListrowname,toString(i))	
		}
	}

	rownames(CharList)=CharListrowname

	DistMat = matrix(Inf, ncol=ObservedNodeNumber, nrow=ObservedNodeNumber,
	dimnames=list(rownames(CharList)[1:ObservedNodeNumber],
	rownames(CharList)[1:ObservedNodeNumber]))

	for (rowi in 1:(ObservedNodeNumber-1))
	{
		for (rowj in (rowi+1):ObservedNodeNumber)
		{
			DistMat[rowi,rowj]=sum(unlist(CharList[rowi,])==unlist(CharList[rowj,]))
			DistMat[rowj,rowi] = DistMat[rowi,rowj]			
		}

	}
	#... find min distance id
	idnew = ObservedNodeNumber
	for (IdRemain in ObservedNodeNumber:3)	
	{
		minid = which.min(DistMat)
		minidcol = ceiling(minid/(IdRemain))
		minidrow = minid - IdRemain*(minidcol-1)
		minidcolname = colnames(DistMat)[minidcol]
		minidrowname = colnames(DistMat)[minidrow]
		idnew = idnew + 1
		idnewstr = toString(idnew)
		NodeList = c(NodeList, minidcolname, minidrowname)
		# 1# function 1
		ParentList[[minidcolname]] = c(ParentList[[minidcolname]], idnewstr)
		NeighbourList[[minidcolname]] = c(NeighbourList[[minidcolname]], idnewstr)
		ParentList[[minidrowname]] = c(ParentList[[minidrowname]], idnewstr)
		NeighbourList[[minidrowname]] = c(NeighbourList[[minidrowname]], idnewstr)
		#2
		KidList[[idnewstr]] = c(KidList[[idnewstr]], minidcolname, minidrowname)
		NeighbourList[[idnewstr]] = c(NeighbourList[[idnewstr]],
		minidcolname, minidrowname)
	
		#... reconstruct matrix
		vectchange = NULL
		for (noderow in colnames(DistMat))
		{
			if ((noderow != minidcolname)&(noderow != minidrowname))
			{
				vectchange = c(vectchange, 0.5*(DistMat[minidrowname, noderow]+
				DistMat[minidcolname, noderow]-
				DistMat[minidrowname, minidcolname]))			
			}else
			{
				vectchange = c(vectchange, Inf)
			}
		}
		DistMat[minidcolname,] = vectchange
		DistMat[,minidcolname] = DistMat[minidcolname,]
		colnames(DistMat)[minidcol] = idnewstr
		rownames(DistMat)[minidcol] = idnewstr
		DistMat = DistMat[,-minidrow]
		DistMat = DistMat[-minidrow,]
	}

	restid = colnames(DistMat)[colnames(DistMat)!=idnewstr]
	rootid = idnewstr
	NodeList = c(NodeList, restid, rootid)
	#1
	ParentList[[restid]] = c(ParentList[[restid]], rootid)
	NeighbourList[[restid]] = c(NeighbourList[[restid]], rootid)
	#2
	KidList[[rootid]] = c(KidList[[rootid]], restid)
	NeighbourList[[rootid]] = c(NeighbourList[[rootid]], restid)

	Initialres <- list("CharList" = CharList, "PositionChar"=PositionChar,
	"KidList"=KidList, "ParentList"=ParentList,	"NeighbourList"=NeighbourList, 
	"NodeList"=NodeList, "PositionDiff"=PositionDiff, 
	"AllNodeNumber"=AllNodeNumber,
	"PositionProb"=PositionProb,"TextLen"=TextLen)
	invisible(Initialres)
}

LinkMatf81 <- function(NodeNumber, CharList, PositionChar, KidList, ParentList, 
NeighbourList, NodeList, PositionDiff,
PositionProb, delta, TextLen, approximation)
{
	localtimer=0
	LinkMatAll = matrix(0, ncol= NodeNumber, nrow = NodeNumber)
	colnames(LinkMatAll) = NodeList
	rownames(LinkMatAll) = NodeList
	#ProbTree = 0

	for (Position in 1:TextLen)
	{

		if (PositionDiff[Position]>1)
		{


			PositionDiffTmp = PositionDiff[Position]
			PositionCharTmp = PositionChar[[Position]]
			######################### different from other models ##############
			# prob change mat	
			tmp = PositionProb[[Position]]
			ProbChangeMat = matrix(0,ncol=PositionDiffTmp,nrow=PositionDiffTmp)
			colnames(ProbChangeMat) = PositionCharTmp
			rownames(ProbChangeMat) = PositionCharTmp
			for (ci in PositionCharTmp)
			{
				ProbChangeMat[ci,] = 0.1*tmp[ci]
			}
			diag(ProbChangeMat)=1-0.1*(1-tmp)
			# log matrix
			LogMat = log(t(ProbChangeMat))-matrix(log(PositionProb[[Position]]),
			ncol=PositionDiffTmp,nrow=PositionDiffTmp,byrow=TRUE)
			#
			######################### different from other models ##############
			LinkMat = matrix(-Inf, ncol= NodeNumber, nrow = NodeNumber)
			colnames(LinkMat) = NodeList
			rownames(LinkMat) = NodeList

			UMat = array(0,dim=c(NodeNumber,NodeNumber,PositionDiffTmp),
			dimnames=list(NodeList,NodeList,PositionCharTmp))
			uMat = array(0,dim=c(NodeNumber,NodeNumber,PositionDiffTmp),
			dimnames=list(NodeList,NodeList,PositionCharTmp))

			ProbMat = array(0,dim=c(NodeNumber,NodeNumber,PositionDiffTmp,
			PositionDiffTmp),dimnames=list(NodeList,NodeList,PositionCharTmp,
			PositionCharTmp))
		
	
			# up
			for (i in NodeList[1:NodeNumber])
			{
				if (length(ParentList[[i]])>0)
				{
					CharTmp = CharList[i,Position]
					CharParent = CharList[ParentList[[i]], Position]
					# U
					if (length(KidList[[i]]) == 0)# no kid
					{					
						if (CharTmp != "?")
						{	
							UMat[i,ParentList[[i]],CharTmp] = 1	
						}else
						{
							UMat[i,ParentList[[i]],] = 1
						}
					}else # have kid
					{
						if (CharTmp != "?")
						{
							UMat[i,ParentList[[i]],CharTmp] = 1
						}else				
						{
							tmp = 1
							for (j in KidList[[i]])
							{
									tmp = tmp*uMat[j,i,]
							}
							UMat[i,ParentList[[i]],] = tmp 
						}	
					}				 
					# u
					uMat[i,ParentList[[i]],]=
					UMat[i,ParentList[[i]],]%*%ProbChangeMat 
				}
			}
	
			#down
			for (i in NodeList[NodeNumber:1])
			{
				CharTmp = CharList[i,Position]
				if (length(KidList[[i]]) != 0) 
				{
					NeighbourTmp = NeighbourList[[i]]
					KidTmp = KidList[[i]]			
					for (j in KidTmp)
					{
						CharKidTmp = CharList[j,Position]
						if (CharTmp == "?")
						{
							tmp = 1
							for (k in NeighbourTmp[NeighbourTmp!=j])
							{
								tmp = tmp*uMat[k,i,]
							}
							UMat[i,j,] = tmp
						}else
						{
							UMat[i,j,CharTmp] = 1
						} 
						uMat[i,j,]=UMat[i,j,]%*%ProbChangeMat 
					}	
				} 
			}

			#prob of leaf
			#probtmp = NULL
			for (i in NodeList)
			{
				tmp = PositionProb[[Position]]*
				UMat[i,NeighbourList[[i]][1],]* uMat[NeighbourList[[i]][1],i,]	
				ProbMat[i,i,,1] = tmp/sum(tmp)
			}
			
			 #ProbTree = ProbTree+log(sum(tmp))
		
			#2 prob of linked nodes
			for (i in NodeList[NodeNumber:1])
			{
				if (length(KidList[[i]]) > 0)
				{
					for (j in KidList[[i]])
					{							
						ProbMat[i,j,,]=matrix(PositionProb[[Position]],
						nrow=PositionDiffTmp,ncol=PositionDiffTmp)*
						(t(t(UMat[i,j,]))%*%(t(UMat[j,i,])))*(t(ProbChangeMat))
						ProbMat[i,j,,] = ProbMat[i,j,,]/(sum(ProbMat[i,j,,]))
						ProbMat[j,i,,]=t(ProbMat[i,j,,])
					}	
				}
			}

			if (approximation == 0)
			{
			#3 prob of all nodes
				for (i in (NodeNumber-1):1)
				{
					for (j in (i+1):NodeNumber)
					{ 
						if (NodeList[j] != ParentList[[ NodeList[i] ]])
						{
							tmp = (ProbMat[NodeList[i],
							ParentList[[ NodeList[i] ]],,]/
							matrix(ProbMat[ParentList[[ NodeList[i] ]],
							ParentList[[ NodeList[i] ]],,1],
							nrow=PositionDiffTmp,ncol=PositionDiffTmp,byrow=TRUE)) 
							tmp[is.na(tmp)]=0
							ProbMat[NodeList[i],NodeList[j],,]=
							tmp %*% ProbMat[ParentList[[ NodeList[i] ]],
							NodeList[j],,]
							ProbMat[NodeList[j],NodeList[i],,]=
							t(ProbMat[NodeList[i],NodeList[j],,])		
						}
					}
				} 
			}else
			{
				for (i in (NodeNumber-1):1)
				{

					for (j in (i+1):NodeNumber)
					{ 

						if (NodeList[j] != ParentList[[ NodeList[i] ]])
						{
							tmp1 = ProbMat[NodeList[i],NodeList[i],,1]
							tmp2 = ProbMat[NodeList[j],NodeList[j],,1]
							tmp1[is.na(tmp)]=0
							tmp2[is.na(tmp)]=0
						
							ProbMat[NodeList[i],NodeList[j],,]=tmp1 %*% t(tmp2)
							ProbMat[NodeList[j],NodeList[i],,]=
							t(ProbMat[NodeList[i],NodeList[j],,])		
						}
					}
				}					 
			}

			for (i in 1:(NodeNumber-1))
			{
				for (j in (i+1):NodeNumber)
				{
					LinkMat[NodeList[i],NodeList[j]] = 
					sum(ProbMat[NodeList[i],NodeList[j],,]*LogMat)
					LinkMat[NodeList[j],NodeList[i]] = 
					LinkMat[NodeList[i],NodeList[j]]
				}
			}
			LinkMatAll = LinkMatAll+LinkMat		
		}
	}

	noise = rnorm(NodeNumber*(NodeNumber-1)/2, sd=delta)
	k = 1
	LinkMatAllori = LinkMatAll

	for (i in 1:(NodeNumber-1))
	{
		for (j in (i+1):NodeNumber)
		{
			LinkMatAll[NodeList[i],NodeList[j]] = 
			LinkMatAll[NodeList[i],NodeList[j]]+noise[k]
			LinkMatAll[NodeList[j],NodeList[i]] = 
			LinkMatAll[NodeList[i],NodeList[j]]
			k=k+1
		}
	}

	LinkMatAllres = list("LinkMatAll"=LinkMatAll, "LinkMatAllori"=LinkMatAllori)
	invisible(LinkMatAllres)
}

MTreef81 <- function(AllNodeNumber, LinkMatAllori,LinkMatAll)
{
	NodeList = colnames(LinkMatAll)
	NodeLinkedSign = rep(FALSE,AllNodeNumber)
	names(NodeLinkedSign) = NodeList
	NodeLinkedSign[NodeList[AllNodeNumber]]=TRUE

	PathList = vector("list", AllNodeNumber)
	names(PathList) = NodeList
	i=1
	qscore = 0
	while (i<AllNodeNumber)
	{
		NodeRemain = NodeList[!NodeLinkedSign]
		NodeLinked = NodeList[NodeLinkedSign]
		tmp = which.max(LinkMatAll[NodeLinked,NodeRemain])

		LinkMatAlloritmp = LinkMatAllori[NodeLinked,NodeRemain]
		qscore = qscore+LinkMatAlloritmp[tmp]
		To = NodeRemain[ceiling(tmp/length(NodeLinked))]
		From = NodeLinked[tmp-
		(ceiling(tmp/length(NodeLinked))-1)*length(NodeLinked)]
		NodeLinkedSign[[To]] = TRUE
		PathList[[From]] = c(PathList[[From]],To)
		PathList[[To]] = c(PathList[[To]],From)
		i=i+1	 
	}

	########## reorder
	Root = NodeList[AllNodeNumber]
	NodeListNew = c(Root)
	i = 1
	ParentListNew = list()
	KidListNew = list()
	NeighbourList = PathList
	while (i<AllNodeNumber)
	{
		for (j in PathList[[NodeListNew[i]]])
		{
			if (length(ParentListNew[[NodeListNew[i]]])>0)
			{ 
				if (j != ParentListNew[[NodeListNew[i]]])
				{
					NodeListNew = c(NodeListNew, j)
					ParentListNew[[j]] = NodeListNew[i]
					KidListNew[[NodeListNew[i]]] = c(KidListNew[[NodeListNew[i]]], j)
				}
			}else 
			{
				NodeListNew = c(NodeListNew, j)
				ParentListNew[[j]] = NodeListNew[i]
				KidListNew[[NodeListNew[i]]] = c(KidListNew[[NodeListNew[i]]], j)
			}
		}
		i = i+1
	}

	ParentList = ParentListNew
	KidList = KidListNew
	NodeList = rev(NodeListNew)

	StrOut = NULL
	for (i in NodeList)
	{
		if (length(ParentList[[i]])>0)
		{
			StrOut = paste(StrOut, i, "\t", ParentList[[i]],"\n",sep="")
		}
	}

	MTreeres <- list("ParentList"=ParentList, "KidList"=KidList, 
	"NeighbourList"=NeighbourList, "NodeList"=NodeList,"qscore"=qscore)
	invisible(MTreeres)
}



# best tree
# last tree (current tree)



iterationrun <- function(runmax, approximation, runres, bestres, iter, converge)
{ 
	f81iteration <- function (MTreef81res,rhoin,deltain,qscorevector,Initialres,approximationin)
	{
		Sys.setlocale(locale="C")
		deltain = deltain*rhoin
		LinkMatf81res <- LinkMatf81(NodeNumber = Initialres[["AllNodeNumber"]], 
		CharList = Initialres[["CharList"]] , 
		PositionChar=Initialres[["PositionChar"]],
		KidList=MTreef81res[["KidList"]], 
		ParentList=MTreef81res[["ParentList"]],	
		NeighbourList=MTreef81res[["NeighbourList"]], 
		NodeList=MTreef81res[["NodeList"]], 
		PositionDiff=Initialres[["PositionDiff"]],
		PositionProb= Initialres[["PositionProb"]], delta = deltain, 
		TextLen=Initialres[["TextLen"]],
		approximation = approximationin)

		MTreef81res <- MTreef81(AllNodeNumber=Initialres[["AllNodeNumber"]],
		LinkMatAllori=LinkMatf81res[["LinkMatAllori"]],
		LinkMatAll=LinkMatf81res[["LinkMatAll"]]) 
		qscorevector = c(qscorevector,MTreef81res[["qscore"]])

		f81iterationres=list("MTreef81res"=MTreef81res,"rhoin"=rhoin,
		"deltain"=deltain,"qscorevector"=qscorevector,"Initialres"=Initialres)
		invisible (f81iterationres)
	}

	itertime = NULL

	runrestmp = list()
	for (run in c(1:runmax))
	{	
		# record time for each iteration
		starttimetmp = Sys.time()
		
		# test if qscore converged
		qscorevectortmp = runres[[run]][["qscorevector"]]
		if ((length(qscorevectortmp)>5)&(converge[run]==0))
		{
			qscorechangevect = qscorevectortmp[(length(qscorevectortmp)-4):length(qscorevectortmp)] - 
			qscorevectortmp[(length(qscorevectortmp)-5):(length(qscorevectortmp)-1)]
			qscorechange = sum(qscorechangevect**2)
		}
		if (length(qscorevectortmp)<=5)
		{
			qscorechange = Inf
		}
		if (converge[run]==1)
		{
			qscorechange = 0
		}

		
		if (qscorechange > 0.00001) # if qscore not converged
		{
			MTreef81res = runres[[run]][["MTreef81res"]]
			rhoin = runres[[run]][["rhoin"]]
			deltain = runres[[run]][["deltain"]]
			qscorevector = runres[[run]][["qscorevector"]]
			Initialres = runres[[run]][["Initialres"]]

			runrestmp[[run]] = f81iteration(MTreef81res=MTreef81res,rhoin=rhoin,deltain=deltain,
			qscorevector=qscorevector,Initialres=Initialres,approximationin=approximation)

			#record the best results
			qscorevectortmp = runrestmp[[run]][["qscorevector"]]
			if (which.max(qscorevectortmp)==length(qscorevectortmp))
			{
				bestrestmp = list()
				bestrestmp[["iter"]] = iter

				bestrestmp[["qscore"]] = runrestmp[[run]][["qscorevector"]][[iter]]
				bestrestmp[["MTreef81res"]] = runrestmp[[run]][["MTreef81res"]]
				bestres[[run]] = bestrestmp
			}
			
			# record time for each iteration		
			endtimetmp = Sys.time()
			itertime = c(itertime,endtimetmp-starttimetmp)		
		}else # if qscore converged
		{
			runrestmp[[run]] = runres[[run]]
			qscorevectortmp = runres[[run]][["qscorevector"]]
			temp = qscorevectortmp[length(qscorevectortmp)]
			qscorevectortmp = c(qscorevectortmp, temp)
			runrestmp[[run]][["qscorevector"]] = qscorevectortmp
			converge[run] = 1
		}
	
	}
	runres = runrestmp

	iterationrunres = list("bestres"=bestres,"runres"=runres,"itertime"=itertime, "converge"=converge)
	invisible (iterationrunres)

}

# 2 The initiation for all runs
initiationrun <- function(runmax, itermax, filein, approximation)
{

	f81initiation <- function(itermaxin, filein, approximationin)
	{
		rhoin = 0.05**(2/itermaxin)
		Sys.setlocale(locale="C")

		Initialres <- Initialf81(fileread = filein)
		deltain = 0.1		
		LinkMatf81res <- LinkMatf81(NodeNumber = Initialres[["AllNodeNumber"]], 
		CharList = Initialres[["CharList"]] , 
		PositionChar=Initialres[["PositionChar"]],
		KidList=Initialres[["KidList"]], 
		ParentList=Initialres[["ParentList"]],	
		NeighbourList=Initialres[["NeighbourList"]], 
		NodeList=Initialres[["NodeList"]], 
		PositionDiff=Initialres[["PositionDiff"]],
		PositionProb= Initialres[["PositionProb"]], delta = deltain, 
		TextLen=Initialres[["TextLen"]], 
		approximation = approximationin)

		MTreef81res <- MTreef81(AllNodeNumber=Initialres[["AllNodeNumber"]],
		LinkMatAllori=LinkMatf81res[["LinkMatAllori"]],
		LinkMatAll=LinkMatf81res[["LinkMatAll"]])
		qscorevector = c(MTreef81res[["qscore"]])

		linkmattmp = LinkMatf81res[["LinkMatAllori"]]
		linkmattmp[linkmattmp==-Inf]=0
		linkmattmp=abs(linkmattmp)
		deltain = max(linkmattmp)*0.1

		f81initialrunres=list("MTreef81res"=MTreef81res,"rhoin"=rhoin,
		"deltain"=deltain,"qscorevector"=qscorevector,"Initialres"=Initialres)
		invisible(f81initialrunres) 
	}

	runres = list()
	bestres = list()
	for (run in c(1:runmax))
	{
		
		runres[[run]]=f81initiation(itermaxin=itermax, filein=filein, 
		approximationin=approximation)	

		bestrestmp = list()
		bestrestmp[["iter"]] = 1
		bestrestmp[["qscore"]] = runres[[run]][["qscorevector"]][1]
		bestrestmp[["MTreef81res"]] = runres[[run]][["MTreef81res"]]
		bestres[[run]] = bestrestmp
	}
	converge = rep(0, runmax)
	initiationrunres = list("bestres"=bestres,"runres"=runres, "converge"=converge)
		
	invisible (initiationrunres)
}

findbestrun <- function(iterationrunres, runmax)
{
	bestrestmp = iterationrunres[["bestres"]]
	bestscoretmp = NULL
	for (run in c(1:runmax))
	{
		bestscoretmp = c(bestscoretmp, bestrestmp[[run]][["qscore"]])
	}
	bestruntmp = which.max(bestscoretmp)
	invisible (bestruntmp)
}

findbestlastrun <- function(iterationrunres, runmax)
{
	bestrestmp = iterationrunres[["runres"]]
	bestscoretmp = NULL
	for (run in c(1:runmax))
	{
		tmp = bestrestmp[[run]][["qscorevector"]]
		bestscoretmp = c(bestscoretmp, tmp[length(tmp)])
	}
	bestruntmp = which.max(bestscoretmp)
	invisible (bestruntmp)
}

updateres <- function(runmax, bestruntmp, iterationrunres)
{
	bestrestmp = iterationrunres[["bestres"]]
	for (run in c(1:runmax))
	{
		iterationrunres[["bestres"]][[run]] = bestrestmp[[bestruntmp]] 
		#### update "bestres"
		iterationrunres[["runres"]][[run]][["MTreef81res"]] = bestrestmp[[bestruntmp]] [["MTreef81res"]] 
		#### update "runres"--"MTreef81res"
		qscorevectortmp = iterationrunres[["runres"]][[run]][["qscorevector"]]
		qscorevectortmp = c(qscorevectortmp, bestrestmp[[bestruntmp]] [["qscore"]])
		iterationrunres[["runres"]][[run]][["qscorevector"]] = qscorevectortmp
		#### update "runres"--"qscorevector"
	}
	invisible (iterationrunres)
}
