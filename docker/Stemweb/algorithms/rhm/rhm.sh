if test ! -z $1 && test -e $1
then
    file=$1
else
    file=sankoff-tree_0.dot
fi

# internal nodes labeled
#sed -E 's/(^[^ ]*) \[label=\"f:.*\"];/\1 \[label=\"\" shape=point\]; \100 \[label=\"i\1\" shape=plaintext style=dotted fontcolor=grey15\]; \1 -- \100 \[len=0.4 style=invis\];/g' <$file >sankoff-tree_noint.dot

# internal nodes not labeled
sed -E 's/(^[^ ]*) \[label=\"f:.*\"];/\1 \[label=\"\" shape=point\];/g' <$file | sed 's/len=/foolen=/g' >sankoff-tree_noint.dot

awk -v ROOT=i70:i103 -f quartet2nexus.awk $file >sankoff-tree.tre
neato -Tpdf -Gstart=rand -Gcenter -Gepsilon=0.00001 -Gorientation=portrait -Gsize=9,7! -o sankoff-tree.pdf sankoff-tree_noint.dot
