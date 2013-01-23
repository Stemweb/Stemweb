#!/bin/bash

# This script is created to easily(?) install Stemweb on different servers. You need
# to have pip (requires setuptools) and python 2.7 installed before you can use this 
# script. Check details from README.
#
# Script takes a single command line argument which is a path to the python 2.7 
# install. Default is "/usr/bin/python2.7".

${PYTHON27:=$1}
${PYTHON27:="/usr/bin/python2.7"}

# Prompt and exit if pip does not exist.
command -v pip >/dev/null 2>&1 || { echo >&2 "pip is not installed. Check README for details."; exit 1; }
  
pip install --user virtualenv==1.7.2

# Create new virtualenv 'path/to/this/folder/stemenv' and activate it.
virtualenv --distribute --no-site-packages --python=$PYTHON27 stemenv
source ./stemenv/bin/activate

# If we are running on OSX we only install light version of requirements
if [ "$OSTYPE" = "darwin11" ]
then	
	pip install -r requirements.txt
	echo
	echo
	echo "You are running on OSX. You need to manually download and install"
	echo "numpy 1.5.1, matplotlib 1.1.0 and scipy 0.10.1 into ./stemenv"
	echo "virtualenv. Check README for details."
	echo
	echo
elif [ "$OSTYPE" = "linux-gnu" ]
then
	# install numpy first because of dependencies in scipy and matplotlib.
	pip install numpy==1.5.1
	pip install matplotlib==1.1.0
    	pip install scipy==0.10.1
	pip install -r requirements.txt
else
	echo 
	echo "Unsupported OS type. Aborting."
	echo 
	deactivate
	exit 1
fi

# Go to root of Stemweb installation and run database syncing, etc
cd ..
python manage.py syncdb
python manage.py loaddata bootstrap

# Deactivate virtualenv for now.
#deactivate 



