compress=gzip

c1=0
for file1 in _ $*
do
  c1=$(expr $c1 + 1)
  file1stem=$(echo $file1 | sed 's/^.*\///')
  c2=0
  for file2 in $*
  do
    c2=$(expr $c2 + 1)
    file2stem=$(echo $file2 | sed 's/^.*\///')
    if test $file1 = _
    then
	printf "%s " $file2stem
    else
	#if test $c1 -eq $c2
	#then
	#    printf "%d " $(cat $file1 | $compress - | wc -c)
	#else
	    Kxy=$(cat $file1 $file2 | $compress - | wc -c)
#	    Kyx=$(cat $file2 $file1 | $compress - | wc -c)
	    Kx=$(cat $file1 | $compress - | wc -c)
#	    Ky=$(cat $file2 | $compress - | wc -c)
#	    printf "%d " $(expr $Kxy + $Kyx - $Kx - $Ky)
	    printf "%d " $(expr $Kxy - $Kx)
#	    ./NCD $Kxy $Kx $Ky
	#fi
    fi
  done
  echo
done
    
