#!/bin/bash

while read line
do
    color=$(echo $line | cut -f 1 -d ' ')
    nodes=$(echo $line | cut -f 2- -d ' ' -s)
    for node in $nodes
    do
	echo "/label=\"$node\"/ {gsub(\"color=[^ ]*]\",\"color=$color]\");}"
    done
done
echo "{print;}"
