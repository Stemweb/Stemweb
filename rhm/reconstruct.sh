dotfile=$1
dir=allsk
chunksize=11

nos=$(awk '$1 ~ "[:digit:]*" && $2 ~ "f:" {printf "%s ", $1;}' $dotfile)

for no in $nos
do
  ./compose.sh $1 $no $chunksize >reconstructions/i$no
  echo done $no: $(head -10 reconstructions/i$no | tail -1) $(head -11 reconstructions/i$no | tail -1) $(head -12 reconstructions/i$no | tail -1) $(head -13 reconstructions/i$no | tail -1)
done
