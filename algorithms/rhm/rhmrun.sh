#!/bin/bash

# input folder output folder iteration 
foldersan= /Users/slinkola/STAM/Stemweb/algorithms/rhm/
folderin=/Users/slinkola/STAM/Stemweb/algorithms/rhm/test/
folderres=/Users/slinkola/STAM/Stemweb/algorithms/rhm/res/
iterationnumber=250

# logfiles
echo 'start at: ' > $folderin.log
echo `date` >> $folderin.log
echo 'infile: ' >> $folderin.log
echo $folderin >> $folderin.log
echo 'outfile: ' >> $folderin.log
echo $folderres >> $folderin.log


# run
/Users/slinkola/STAM/Stemweb/algorithms/rhm/binarysankoff $folderin/$fn $folderres $iterationnumber 1
/Users/slinkola/STAM/Stemweb/algorithms/rhm/graph.sh


# logfiles
echo 'end at: ' >> $folderin.log
echo `date` >> $folderin.log	


# save results
mv $folderin.log $folderres
mv sankoff-tree_0.dot $folderres/sankoff-tree_0.dot
mv $folderin/sankoff-tree_0.dot $folderres
mv sankoff-tree_noint.dot $folderin.sankoff-tree_noint.dot
mv $folderin.ankoff-tree_noint.dot $folderres
mv sankoff-tree.tre $folderin.sankoff-tree.tre
mv $folderin.sankoff-tree.tre $folderres
mv dendro.dot $folderin.dendro.dot
mv $folderin.dendro.dot $folderres
mv dendro.ps $folderin.dendro.ps
mv $folderin.dendro.ps $folderres
mv sankoff-tree.ps $folderin.sankoff-tree.ps
mv $folderin.sankoff-tree.ps $folderres
mv sankoff-tree.pdf $folderin.sankoff-tree.pdf
mv $folderin.sankoff-tree.pdf $folderres




