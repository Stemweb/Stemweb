file=$1
node=$2
chunksize=$3
label=$(grep "^$node \[" $file | cut -d '"' -f 2)
src=$(echo $label | sed 's/\\n/:/g' | tr ':.' '\n\n')
offset=0
for s in $src
do
  if test $s == 'f'
  then
      continue
  fi
  offset=$(expr $offset + $chunksize)
  if test $s == '-'
  then
      for (( i=0 ; i < $chunksize; i = $(expr $i + 1) ))
      do
	echo
      done
  else
      len=$(cat allsk/$s | wc -l)
      if test $offset -gt $len
      then
	  tail=$(expr $len - $offset)
      else
	  tail=0
      fi
      tail=$(expr $tail + $chunksize)
      head -$offset allsk/$s | tail -$tail
  fi
done
