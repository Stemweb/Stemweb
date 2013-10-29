pkglib_LTLIBRARIES = binarysankoff.so
binarysankoff_so_LDFLAGS = -module -avoid-version -shared


binarysankoff:	
	gcc -lz binarysankoff.c -o binarysankoff

NCD:
	gcc -lz NCD.c -o NCD
	
osx:
	gcc -dynamiclib -Wall -I/usr/include/python2.7/ -lpython2.7 -lz -o binarysankoff_osx.dylib binarysankoff_osx.c 
	mv ./binarysankoff_osx.dylib ./binarysankoff.so

users:
	gcc -I/usr/include/python2.6/ -lpython2.6 -I/usr/include -L/usr/lib -fPIC -g -Wall -c binarysankoff_linux.c
	gcc -shared -fPIC -Wall -I/usr/include -L/usr/lib binarysankoff_linux.o -o binarysankoff.so -lz

linux:	
	gcc -I/usr/include/python2.7/ -lpython2.7 -I/usr/include -L/usr/lib -fPIC -g -Wall -c binarysankoff_linux.c
	gcc -shared -fPIC -Wall -I/usr/include -L/usr/lib binarysankoff_linux.o -o binarysankoff.so -lz
