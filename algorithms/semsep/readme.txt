1 Initialf81 <- function (fileread)
Initiation of tree, probability

2 LinkMatf81 <- function(NodeNumber, CharList, PositionChar, KidList, ParentList, 
Calculation of score matrix

3 MTreef81 <- function(AllNodeNumber, LinkMatAllori,LinkMatAll)
Find best tree from score matrix

4 initiationrun <- function(runmax, itermax, filein, approximation)
First iteration after initiation of tree, to calculate the delta based on maximum value of iteration.

5 iterationrun <- function(runmax, approximation, runres, bestres, iter)
Other iteration except first iteration

6 
findbestrun <- function(iterationrunres, runmax)
Find the run with best result

7 updateres <- function(runmax, bestruntmp, iterationrunres)
Start all iteration from current best result 



initiationrun --> iterationrun --> 
findbestrun --> updateres --> iterationrun

_____________________________________________

Result is in
iterationrunres
= list('bestres'=bestres,'runres'=runres,'itertime'=itertime)

