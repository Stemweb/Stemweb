runsemf81<-function(infile, outfolder, runmax, itermaxin, approximationin=0)
{

	# function 1

	Initialf81 <- function (fileread)
	{
		Dataraw = readLines(fileread)
		datastart=1
		for (i in 1:length(Dataraw))
		{
			if (length(grep('matrix',Dataraw[i]))>0)
			{
				datastart = i+1
				break
			}
		}
		dataend=length(Dataraw)
		for (i in length(Dataraw):1)
		{
			if (length(grep('end',Dataraw[i]))>0)
			{
				dataend = i-1
				break
			}
		}
	
		Data=NULL
		for (i in datastart:dataend)
		{
			linetmp=Dataraw[i]
			linetmp=gsub(' ','\t',linetmp)
			linetmp=gsub(';','',linetmp)
			linetmp=unlist(strsplit(linetmp,split='\t'))
			linetmpj=NULL
			for (linetmpi in linetmp)
			{
				if ((length(linetmpi)>0)&(linetmpi!=''))
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
			
			if (sum(namestmp=='?')==1)
			{
			unkowntmp = tmp[namestmp=='?']
			tmp = tmp[namestmp!='?'] # exclude the unknown character		
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
				tmp = rep('?',TextLen)
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

		Initialres <- list('CharList' = CharList, 'PositionChar'=PositionChar,
		'KidList'=KidList, 'ParentList'=ParentList,	'NeighbourList'=NeighbourList, 
		'NodeList'=NodeList, 'PositionDiff'=PositionDiff, 
		'AllNodeNumber'=AllNodeNumber,
		'PositionProb'=PositionProb,'TextLen'=TextLen)
		invisible(Initialres)
	}
	

























	#_________function 2____________________________________________________________________________

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
				beg1=Sys.time()
				for (i in NodeList[1:NodeNumber])
				{
					if (length(ParentList[[i]])>0)
					{
						CharTmp = CharList[i,Position]
						CharParent = CharList[ParentList[[i]], Position]
						# U
						if (length(KidList[[i]]) == 0)# no kid
						{					
							if (CharTmp != '?')
							{	
								UMat[i,ParentList[[i]],CharTmp] = 1	
							}else
							{
								UMat[i,ParentList[[i]],] = 1
							}
						}else # have kid
						{
							if (CharTmp != '?')
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
							if (CharTmp == '?')
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

		LinkMatAllres = list('LinkMatAll'=LinkMatAll, 'LinkMatAllori'=LinkMatAllori)
		invisible(LinkMatAllres)
	}



































	#____________function 3_________________________________________________________________________
	MTreef81 <- function(resfolder, iter, AllNodeNumber, LinkMatAllori,LinkMatAll, qscoreold)
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
				StrOut = paste(StrOut, i, '\t', ParentList[[i]],'\n',sep='')
			}
		}
		if (qscoreold<qscore)
		{
			cat(file=paste(resfolder,'/treebest.txt',sep=''), StrOut)
			system(paste('chmod 777 ',resfolder,'/scorelog',sep=''))
			cat(paste(iter,'\n',as.numeric(qscore),'\n','----------','\n'),
			file=paste(resfolder,'/scorelog',sep=''),append=TRUE)
			system(paste('chmod 755 ',resfolder,'/scorelog',sep=''))
		}


		MTreeres <- list('ParentList'=ParentList, 'KidList'=KidList, 
		'NeighbourList'=NeighbourList, 'NodeList'=NodeList,'qscore'=qscore)
		invisible(MTreeres)
	}










































	#______________function 4_______________________________________________________________________	

	allstart <- function (resfolderin, itermaxin,
	filein, approximationin)
	{
		rhoin = 0.05**(2/itermaxin)


		Sys.setlocale(locale="C")

		iternow = 0
		stop = 0
		cat(paste(''),file=paste(resfolderin,'/scorelog',sep=''))


		Initialres <- Initialf81(fileread = filein)


		begTime <- Sys.time()
		deltain = 0.1		
		LinkMatf81res <- LinkMatf81(NodeNumber = Initialres[['AllNodeNumber']], 
		CharList = Initialres[['CharList']] , 
		PositionChar=Initialres[['PositionChar']],
		KidList=Initialres[['KidList']], 
		ParentList=Initialres[['ParentList']],	
		NeighbourList=Initialres[['NeighbourList']], 
		NodeList=Initialres[['NodeList']], 
		PositionDiff=Initialres[['PositionDiff']],
		PositionProb= Initialres[['PositionProb']], delta = deltain, 
		TextLen=Initialres[['TextLen']], 
		approximation = approximationin)

		qscorevector = c(-100000)
		MTreef81res <- MTreef81(resfolder=resfolderin, iter=iternow, 
		AllNodeNumber=Initialres[['AllNodeNumber']],
		LinkMatAllori=LinkMatf81res[['LinkMatAllori']],
		LinkMatAll=LinkMatf81res[['LinkMatAll']], 
		qscoreold=max(qscorevector))
		qscorevector = c(qscorevector,MTreef81res[['qscore']])
		endTime = Sys.time()


		linkmattmp = LinkMatf81res[['LinkMatAllori']]
		linkmattmp[linkmattmp==-Inf]=0
		linkmattmp=abs(linkmattmp)
		deltain = max(linkmattmp)*0.1


		cat(paste('rho\n',rhoin,'\n----------\n',
		'delta\n',deltain,'\n----------\n',
		iternow,'\n',endTime,'\n',begTime,'\n',endTime-begTime,'\n','----------\n',sep=''),
		file=paste(resfolderin,'/','log',sep=''))


		for (iternow in 1:(round(itermaxin*0.1)+1))
		{	
			deltain = deltain*rhoin
			begTime = Sys.time()
			LinkMatf81res <- LinkMatf81(NodeNumber = Initialres[['AllNodeNumber']], 
			CharList = Initialres[['CharList']] , 
			PositionChar=Initialres[['PositionChar']],
			KidList=MTreef81res[['KidList']], 
			ParentList=MTreef81res[['ParentList']],	
			NeighbourList=MTreef81res[['NeighbourList']], 
			NodeList=MTreef81res[['NodeList']], 
			PositionDiff=Initialres[['PositionDiff']],
			PositionProb= Initialres[['PositionProb']], delta = deltain, 
			TextLen=Initialres[['TextLen']], 
			approximation = approximationin)
		
			MTreef81res <- MTreef81(resfolder=resfolderin, iter=iternow, 
			AllNodeNumber=Initialres[['AllNodeNumber']],
			LinkMatAllori=LinkMatf81res[['LinkMatAllori']],
			LinkMatAll=LinkMatf81res[['LinkMatAll']], 
			qscoreold=max(qscorevector))
			qscorevector = c(qscorevector,MTreef81res[['qscore']])			
			endTime <- Sys.time()	
		}
		allstartres=list('MTreef81res'=MTreef81res,'rhoin'=rhoin,
		'deltain'=deltain,'qscorevector'=qscorevector,'Initialres'=Initialres)
		invisible(allstartres)
	 
	}




































	#________________function 5_____________________________________________________________________	
	allend <- function (resfolderin, itermaxin,
	filein, approximationin,
	rhoin,deltain,qscorevector,Initialres,MTreef81res)
	{
		Sys.setlocale(locale="C")
		stop = 0

		for (iternow in c((round(itermaxin*0.1)+2):itermaxin))
		{	
			deltain = deltain*rhoin
			begTime = Sys.time()
			LinkMatf81res <- LinkMatf81(NodeNumber = Initialres[['AllNodeNumber']], 
			CharList = Initialres[['CharList']] , 
			PositionChar=Initialres[['PositionChar']],
			KidList=MTreef81res[['KidList']], 
			ParentList=MTreef81res[['ParentList']],	
			NeighbourList=MTreef81res[['NeighbourList']], 
			NodeList=MTreef81res[['NodeList']], 
			PositionDiff=Initialres[['PositionDiff']],
			PositionProb= Initialres[['PositionProb']], delta = deltain, 
			TextLen=Initialres[['TextLen']],
			approximation = approximationin)
		
			MTreef81res <- MTreef81(resfolder=resfolderin, iter=iternow, 
			AllNodeNumber=Initialres[['AllNodeNumber']],
			LinkMatAllori=LinkMatf81res[['LinkMatAllori']],
			LinkMatAll=LinkMatf81res[['LinkMatAll']], 
			qscoreold=max(qscorevector))
			qscorevector = c(qscorevector,MTreef81res[['qscore']])			
			endTime <- Sys.time()


			if ((iternow<5)|(stop==1)|iternow==itermaxin)
			{
				system(paste('chmod 777 ',resfolderin,'/log',sep=''))
				cat(paste(iternow,'\n',endTime,'\n',begTime,
				'\n',endTime-begTime,'\n','----------\n',sep=''),
				file=paste(resfolderin,'/','log',sep=''),append=TRUE)
				system(paste('chmod 755 ',resfolderin,'/log',sep=''))
			}


			if (stop==1|iternow==itermaxin)
			{
				StrOuttmp=NULL
				for (itmp in MTreef81res[['NodeList']])
				{
					if (length(MTreef81res[['ParentList']][[itmp]])>0)
					{
						StrOuttmp = paste(StrOuttmp, itmp, '\t', MTreef81res[['ParentList']][[itmp]],'\n',sep='')
					}
				}
				cat(file=paste(resfolderin,'/treelast.txt',sep=''), StrOuttmp)
				
				system(paste('chmod 777 ',resfolderin,'/scorelog',sep=''))
				cat(paste(iternow,'\n',as.numeric(qscorevector[length(qscorevector)]),'\n','----------','\n'),
				file=paste(resfolderin,'/scorelog',sep=''),append=TRUE)	
				system(paste('chmod 755 ',resfolderin,'/scorelog',sep=''))		
		
				cat (paste('stop at run ', iternow, '\n', sep=''))
				system(paste('chmod 777 ',resfolderin,'/','log',sep=''))
				cat(paste('stop at run ', iternow, sep=''),
				file=paste(resfolderin,'/','log',sep=''),append=TRUE)
				system(paste('chmod 755 ',resfolderin,'/','log',sep=''))

				invisible (qscorevector)
				break
			}

			if (length(qscorevector)>10)
			{
				qscorechange = 
				(sum(qscorevector[(length(qscorevector)-9):length(qscorevector)])-
				10*qscorevector[length(qscorevector)])/10
			}else
			{
				qscorechange = 10000000
			}
			if ((iternow>(itermaxin*2/3))&(qscorechange<0.0001))
			{		
				stop = 1	
			}
	
		}
		invisible (qscorevector)

	}

	#_____________function 6________________________________________________________________________	


	if (!file.exists(outfolder))
	{
		stop('\n********************************************************\n!Please input the full path of the folder for results\n********************************************************\n', call. = FALSE)
	}
	if (!(file.exists(infile)))
	{
		stop('\n********************************************************\n!Please input the full path of the input data files\n********************************************************\n', call. = FALSE)
	}

	cat (paste('********************************************************\n'))



	filei=unlist(strsplit(infile,'/'))
	filei=filei[length(filei)]
	nexfile = infile
	resfolder = paste(outfolder,'/',filei,sep='')
	unlink(x=resfolder,recursive = TRUE)
	dir.create(path=resfolder, showWarnings = TRUE)
	system(paste('chmod 777 ',resfolder,sep=''))

	allstartres={}
	qscorerunvect=NULL
	idvect=NULL
	for (run in c(1:runmax))
	{
		resfolder2 = paste(outfolder,'/',filei,'/run',run,sep='')

		unlink(x=resfolder2,recursive = TRUE)
		dir.create(resfolder2,showWarnings = TRUE)
		system(paste('chmod 777 ',resfolder2,sep=''))

		allstartres[[paste(run)]]<-allstart(resfolderin = resfolder2, 
		filein = nexfile,
		itermaxin=itermaxin, 
		approximationin=approximationin) 


		qscorevectortmp = allstartres[[paste(run)]][['qscorevector']]
		qscorerunvect=c(qscorerunvect,qscorevectortmp[length(qscorevectortmp)])
		idvect = c(idvect,paste(run))
	}
	
	bestrunid = which.max(qscorerunvect)
	beststartres = allstartres[[idvect[bestrunid]]]

	qscorerun=NULL
	for (run in c(1:runmax))
	{
		
		resfolder2 = paste(outfolder,'/',filei,'/run',run,sep='')
		
		cat (paste('---------------------------------------------------\n',
		infile,' run ',run,'\n',sep=''))		
		qscoreruntmp<-allend(resfolderin = resfolder2, 
		filein = nexfile,
		itermaxin=itermaxin, 
		approximationin=approximationin,
		rhoin=beststartres[['rhoin']],
		deltain=beststartres[['deltain']],
		qscorevector=beststartres[['qscorevector']],
		Initialres=beststartres[['Initialres']],
		MTreef81res=beststartres[['MTreef81res']]) 
		qscorerun<-rbind(qscorerun,c(max(qscoreruntmp),qscoreruntmp[length(qscoreruntmp)]))
	}
	
	
	# save the results
	runlastbest = which.max(qscorerun[,2])
	runbest = which.max(qscorerun[,1])
	file.copy(from=paste(outfolder,'/',filei,'/run',runlastbest,'/treelast.txt',sep=''), 
	to=paste(outfolder,'/',filei,'/lastbest',sep=''))
	file.copy(from=paste(outfolder,'/',filei,'/run',runbest,'/treebest.txt',sep=''), 
	to=paste(outfolder,'/',filei,'/allbest',sep=''))
	cat(paste('lastbest\t',runlastbest,'\t',qscorerun[runlastbest,2],'\n',
	'allbest\t',runbest,'\t',qscorerun[runbest,1],sep=''),
	file=paste(outfolder,'/',filei,'/','resultsummary',sep=''))
	cat (paste('********************************************************\n\n'))
	
	
	# change results to matrix and dot file
	nettomatrix <- function(netfile)
	{
		netin = read.table(netfile,header=FALSE,sep='\t',
		stringsAsFactors=FALSE,colClasses='character')
		nodenames = unique(c(netin[,1],netin[,2]))
		nodenames = sort(nodenames)
		nodenumber = length(nodenames)
		linkmatrix= matrix(-1,ncol=nodenumber,nrow=nodenumber,
		dimnames=list(nodenames,nodenames))
		diag(linkmatrix)=0
		for (i in 1:dim(netin)[1])
		{
			linkmatrix[netin[i,1],netin[i,2]]=1
			linkmatrix[netin[i,2],netin[i,1]]=1
		}
		strout = paste(c(paste(nodenumber),nodenames),collapse='\n')
		strout = paste(c(strout,
		apply(X=linkmatrix,MARGIN=1,function(x) paste(x,collapse=' '))),
		collapse='\n')

		cat(strout,file=paste(netfile,'.matrix',sep=''))
	}


	nettodot <- function(netfile)
	{
		netin = read.table(netfile,header=FALSE,sep='\t',
		stringsAsFactors=FALSE,colClasses='character')
		nodenames = unique(c(netin[,1],netin[,2]))
		nodenames = sort(nodenames)
		nodenumber = length(nodenames)
		strout = 'graph clustering {\n\tsize=\"5,5\"\n'
		for (i in nodenames)
		{
			if (gsub('[0-9]','',i)=='')
			{
				#hidden nodes
				strouttmp = paste('\t',i,' [shape=point];',sep='')
				strout = paste(strout, strouttmp, sep='\n')					
			}else
			{
				#observed nodes
				strouttmp = paste('\t',i, ' [label=\"', i, 
				'\" shape=plaintext fontsize=24];', sep='' )
				strout = paste(strout, strouttmp, sep='\n')				
			}
		}
		strout = paste(strout, '\n', sep='')				

		for (i in 1:dim(netin)[1])
		{
			strouttmp = paste('\t',netin[i,1],' -- ',netin[i,2],';',sep='')
			strout = paste(strout, strouttmp, sep='\n')				
		}
		strout = paste(strout, '}', sep='\n')
		cat(strout,file=paste(netfile,'.dot',sep=''))	
		
		system(paste('neato -Tpdf -Gstart=rand ', 
		netfile,'.dot > ',netfile,'.pdf',sep=''))	
	}

	nettomatrix(netfile=paste(outfolder,'/',filei,'/allbest',sep=''))
	nettodot(netfile=paste(outfolder,'/',filei,'/allbest',sep=''))
	nettomatrix(netfile=paste(outfolder,'/',filei,'/lastbest',sep=''))
	nettodot(netfile=paste(outfolder,'/',filei,'/lastbest',sep=''))



	# rmove permissions
	system(paste('chmod 755 ',resfolder,sep=''))
	for (run in c(1:runmax))
	{		
		resfolder2 = paste(outfolder,'/',filei,'/run',run,sep='')
		system(paste('chmod 755 ',resfolder2,sep=''))
	}

}


	
	
	
	
