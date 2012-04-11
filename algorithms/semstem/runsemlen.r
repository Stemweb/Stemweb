	
#_____________________________________________________________________________________






#_____________________________________________________________________________________	

allstart <- function (resfolderin, windowsin, itermaxin,
filein, method, approximationin, filecsvin, mdlbasein)
{
	rhoin = 0.05**(2/itermaxin)
	print (rhoin)
	dir.create(path=resfolderin)
	Sys.setlocale(locale="C")

	if (method == 'uni')
	{
		iternow = 0
		print (iternow)
		stop = 0
		cat('',	file=paste(resfolderin,'/score','log',sep=''))
		Initialres <- Initialuni(fileread = filein)
		begTime <- Sys.time()
		deltain = 0.1		
		LinkMatunires <- LinkMatuni(NodeNumber = Initialres[['AllNodeNumber']], 
		CharList = Initialres[['CharList']] , 
		PositionChar=Initialres[['PositionChar']],
		KidList=Initialres[['KidList']], 
		ParentList=Initialres[['ParentList']],	
		NeighbourList=Initialres[['NeighbourList']], 
		NodeList=Initialres[['NodeList']], 
		PositionDiff=Initialres[['PositionDiff']], 
		lenmat=Initialres[['lenmat']], 
		PositionProb= Initialres[['PositionProb']], delta = deltain, 
		TextLen=Initialres[['TextLen']], 
		approximation = approximationin)
		qscorevector = c(-100000)

		MTreeunires <- MTreeuni(resfolder=resfolderin, iter=iternow, 
		AllNodeNumber=Initialres[['AllNodeNumber']],
		LinkMatAllori=LinkMatunires[['LinkMatAllori']],
		LinkMatAll=LinkMatunires[['LinkMatAll']], 
		windows=windowsin, itermax=itermaxin,
		qscoreold=max(qscorevector),
		stopin = stop,lenmat=LinkMatunires[['lenmat']])

		qscorevector = c(qscorevector,MTreeunires[['qscore']])

		endTime = Sys.time()
		cat(paste(iternow,'\n',endTime,'\n',begTime,'\n',endTime-begTime,'\n','----------\n',sep=''),file=paste(resfolderin,'/','log',sep=''))
		linkmattmp = LinkMatunires[['LinkMatAllori']]
		linkmattmp[linkmattmp==-Inf]=0
		#linkmattmp[linkmattmp==NaN]=100
		linkmattmp=abs(linkmattmp)
		deltain = max(linkmattmp)*0.1
		#print ('======')
		#print (linkmattmp)
		#print (deltain)

		for (iternow in 1:round(itermaxin*0.1))
		{
			if (round(iternow/100)==iternow/100)
			{
				print (iternow)
			}

			deltain = deltain*rhoin
			begTime = Sys.time()
			LinkMatunires <- LinkMatuni(NodeNumber = Initialres[['AllNodeNumber']], 
			CharList = Initialres[['CharList']] , 
			PositionChar=Initialres[['PositionChar']],
			KidList=MTreeunires[['KidList']], 
			ParentList=MTreeunires[['ParentList']],	
			NeighbourList=MTreeunires[['NeighbourList']], 
			NodeList=MTreeunires[['NodeList']], 
			PositionDiff=Initialres[['PositionDiff']],
			lenmat=LinkMatunires[['lenmat']], 
			PositionProb= Initialres[['PositionProb']], delta = deltain, 
			TextLen=Initialres[['TextLen']],  
			approximation = approximationin)

			MTreeunires <- MTreeuni(resfolder=resfolderin, iter=iternow, 
			AllNodeNumber=Initialres[['AllNodeNumber']],
			LinkMatAllori=LinkMatunires[['LinkMatAllori']],
			LinkMatAll=LinkMatunires[['LinkMatAll']], 
			windows=windowsin, itermax=itermaxin,
			qscoreold=max(qscorevector),
			stopin = stop,lenmat=LinkMatunires[['lenmat']])
			qscorevector = c(qscorevector,MTreeunires[['qscore']])			
			endTime <- Sys.time()
			if ((iternow<5)|(stop==1))
			{
				cat(paste(iternow,'\n',endTime,'\n',begTime,
				'\n',endTime-begTime,'\n','----------\n',sep=''),
				file=paste(resfolderin,'/','log',sep=''),append=TRUE)
				StrOuttmp=NULL
				lenouttmp=NULL
				for (itmp in MTreeunires[['NodeList']])
				{
					if (length(MTreeunires[['ParentList']][[itmp]])>0)
					{
						StrOuttmp = paste(StrOuttmp, itmp, '\t', MTreeunires[['ParentList']][[itmp]],'\n',sep='')
						lenouttmp = paste(lenouttmp, itmp,'\t',MTreeunires[['ParentList']][[itmp]],'\t',
						LinkMatunires[['lenmat']][itmp,MTreeunires[['ParentList']][[itmp]]],'\n',sep='')
					}
				}
				cat(file=paste(resfolderin,'/tree_',iternow,'.txt',sep=''), StrOuttmp)
				cat(file=paste(resfolderin,'/len_',iternow,'.txt',sep=''), lenouttmp)
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
			if (stop == 1)
			{
				print ('stop at')
				print (iternow)
				break
			}
			if ((iternow>(itermaxin*2/3))&(qscorechange<0.0001))
			{		
				stop = 1	
			}	
		}
		allstartres=list('MTreeunires'=MTreeunires,'rhoin'=rhoin,
		'deltain'=deltain,'qscorevector'=qscorevector,
		'Initialres'=Initialres,'LinkMatunires'=LinkMatunires)
		invisible(allstartres)
	} 
}

#_____________________________________________________________________________________	
allend <- function (resfolderin, windowsin, itermaxin,
filein, method, approximationin, filecsvin, mdlbasein,
rhoin,deltain,qscorevector,Initialres,MTreeunires,LinkMatunires)
{

	Sys.setlocale(locale="C")

	if (method == 'uni')
	{
		iternow = round(itermaxin*0.1)+1
		print (iternow)
		stop = 0


		for (iternow in c((itermaxin*0.1+1):itermaxin))
		{
			if (round(iternow/100)==iternow/100)
			{
				print (iternow)
			}

			deltain = deltain*rhoin
			begTime = Sys.time()
			LinkMatunires <- LinkMatuni(NodeNumber = Initialres[['AllNodeNumber']], 
			CharList = Initialres[['CharList']] , 
			PositionChar=Initialres[['PositionChar']],
			KidList=MTreeunires[['KidList']], 
			ParentList=MTreeunires[['ParentList']],	
			NeighbourList=MTreeunires[['NeighbourList']], 
			NodeList=MTreeunires[['NodeList']], 
			PositionDiff=Initialres[['PositionDiff']],
			lenmat=LinkMatunires[['lenmat']], 
			PositionProb= Initialres[['PositionProb']], delta = deltain, 
			TextLen=Initialres[['TextLen']],
			approximation = approximationin)
					
			MTreeunires <- MTreeuni(resfolder=resfolderin, iter=iternow, 
			AllNodeNumber=Initialres[['AllNodeNumber']],
			LinkMatAllori=LinkMatunires[['LinkMatAllori']],
			LinkMatAll=LinkMatunires[['LinkMatAll']], 
			windows=windowsin, itermax=itermaxin,
			qscoreold=max(qscorevector),
			stopin = stop,lenmat=LinkMatunires[['lenmat']])
			qscorevector = c(qscorevector,MTreeunires[['qscore']])			
			endTime <- Sys.time()
			if ((iternow<5)|(stop==1))
			{
				cat(paste(iternow,'\n',endTime,'\n',begTime,
				'\n',endTime-begTime,'\n','----------\n',sep=''),
				file=paste(resfolderin,'/','log',sep=''),append=TRUE)
			}
			if (stop==1)
			{
				StrOuttmp=NULL
				lenouttmp=NULL
				for (itmp in MTreeunires[['NodeList']])
				{
					if (length(MTreeunires[['ParentList']][[itmp]])>0)
					{
						StrOuttmp = paste(StrOuttmp, itmp, '\t', MTreeunires[['ParentList']][[itmp]],'\n',sep='')
						lenouttmp = paste(lenouttmp, itmp,'\t',MTreeunires[['ParentList']][[itmp]],'\t',
						LinkMatunires[['lenmat']][itmp,MTreeunires[['ParentList']][[itmp]]],'\n',sep='')
					}
				}
				cat(file=paste(resfolderin,'/treelast.txt',sep=''), StrOuttmp)
				cat(file=paste(resfolderin,'/lenlast','.txt',sep=''), lenouttmp)
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
			if (stop == 1)
			{
				print ('stop at')
				print (iternow)
				break
			}
			if ((iternow>(itermaxin*2/3))&(qscorechange<0.0001))
			{		
				stop = 1	
			}	
		}
	} 
}

#_____________________________________________________________________________________	
runsem<-function(homefolder, runmax, filesid)
{
	nexfolder=paste(homefolder,'/semdata',sep='')
	files = system(paste('dir -1 ',nexfolder,sep=''),intern=TRUE)
	files = sort(files)
	for (filei in files[filesid])
	{
		nexfile = paste(nexfolder,'/',filei,sep='')
		resfolder = paste(homefolder,'/semres/',filei,sep='')
		system(paste('rm -fr ',resfolder,sep=''),intern=TRUE)
		system(paste('mkdir ',resfolder,sep=''),intern=TRUE)
		setwd(resfolder)

		allstartres={}
		qscorerunvect=NULL
		idvect=NULL
		for (run in c(1:runmax))
		{
			resfolder2 = paste(homefolder,'/semres/',filei,'/run',run,sep='')
			system(paste('rm -fr ',resfolder2,sep=''),intern=TRUE)
			system(paste('mkdir ',resfolder2,sep=''),intern=TRUE)

			allstartres[[paste(run)]]<-allstart(resfolderin = resfolder2, 
			filein = nexfile,
			windowsin = 0, itermaxin = 500, 
			method = 'uni',
			approximationin = 0) 


			qscorevectortmp = allstartres[[paste(run)]][['qscorevector']]
			qscorerunvect=c(qscorerunvect,qscorevectortmp[length(qscorevectortmp)])
			idvect = c(idvect,paste(run))
		}
		
		bestrunid = which.max(qscorerunvect)
		beststartres = allstartres[[idvect[bestrunid]]]


		for (run in c(1:runmax))
		{
			resfolder2 = paste(homefolder,'/semres/',filei,'/run',run,sep='')

			allend(resfolderin = resfolder2, 
			filein = nexfile,
			windowsin = 0, itermaxin = 500, 
			method = 'uni',
			approximationin = 0,
			rhoin=beststartres[['rhoin']],
			deltain=beststartres[['deltain']],
			qscorevector=beststartres[['qscorevector']],
			Initialres=beststartres[['Initialres']],
			MTreeunires=beststartres[['MTreeunires']],
			LinkMatunires=beststartres[['LinkMatunires']]) 
		}
		save.image(file='bk.RData')
		setwd(homefolder)
	}
}


runsem(homefolder='/home/fs/zou/Documents/work/stam/structuralem/SEM_R27_len', runmax=3, filesid=c(1))
	
#nohup R CMD BATCH run_1_10.r run_1_10.out >nohup_1_10.out &	
	
	
	
	
