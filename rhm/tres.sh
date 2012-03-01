if test ! -z "$1"
then
    dir=$1
else
    dir=.
fi

rm -f intree
touch intree
for (( i=0; i < 100; i = $(expr $i + 1)))
do
  if test -e $dir/sankoff-tree_$i.dot
  then
      awk -f quartet2nexus.awk $dir/sankoff-tree_$i.dot >>intree
  fi
done
