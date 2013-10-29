if test ! -z $1 && test -e $1
then
    file=$1
else
    file=sankoff-tree_0.dot
fi

# internal nodes labeled
#sed -r 's/(^[^ ]*) \[label=\"f:.*\"];/\1 \[label=\"\" shape=point\];\n\100 \[label=\"i\1\" shape=plaintext style=dotted fontcolor=grey15\];\n\1 -- \100 \[len=0.4 style=invis\];/g' <$file >sankoff-tree_noint.dot

# internal nodes not labeled
sed -r 's/(^[^ ]*) \[label=\"f:.*\"];/\1 \[label=\"\" shape=point\];/g' <$file >sankoff-tree_noint.dot

awk -vJOINLATE=1 -vROOT=i70:i103 -f quartet2dendro.awk $file >dendro.dot
awk -vROOT=i70:i103 -f quartet2nexus.awk $file >sankoff-tree.tre
neato -Tps -Gstart=rand -Gcenter -Gepsilon=0.00001 -Gorientation=portrait -Gsize=9,7! -o sankoff-tree.ps sankoff-tree_noint.dot
neato -Gsize=7,8! -Tps -o dendro.ps dendro.dot
neato -Tpdf -Gstart=rand -Gcenter -Gepsilon=0.00001 -Gorientation=portrait -Gsize=9,7! -o sankoff-tree.pdf sankoff-tree_noint.dot
