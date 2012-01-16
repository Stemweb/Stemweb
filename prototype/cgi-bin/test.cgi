#!/usr/bin/env python
# -*- coding: utf-8 -*-

# enable debugging
import cgitb
import subprocess
from subprocess import call
cgitb.enable()




print "Content-Type: text/plain;charset=utf-8"
print

p = subprocess.Popen('ls -l', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()

#p = subprocess.Popen(['R', 'CMD', 'BATCH', ''], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# print image
#data = open('image.png', 'rb').read()
#print "Content-Type: image/png\nContent-Length: %d\n" % len(data)
#print data