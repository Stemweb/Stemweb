body=$(echo $1 | sed 's/\.[^\.]*$//')
echo $body
rm -r -f $body
mkdir $body

l=$(grep -v 'LECTIO' $1 | wc -l)
l=$(expr $l - 1)

names=$(head -1 $1)
n=$(echo $names | wc -w)
echo $n
i=0
for f in $names
do
  f=$(echo $f | sed 's/ä/ae/g' | sed 's/ö/oe/g')
  i=$(expr $i + 1)
  grep -v 'LECTIO' $1 | cut -f $i | tail -$l | sed 's/TUHO//g' | sed 's/POIS//g' | sed 's/PUUT//g' | sed 's/\*//g' >$body/$f
done
