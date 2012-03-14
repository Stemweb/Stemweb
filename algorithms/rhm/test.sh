#!/bin/bash
DIR="test"
 
if [ -d "$DIR" ]
then
	echo "$DIR directory  exists!"
else
	echo "$DIR directory not found!"
fi

