pkglib_LTLIBRARIES = binarysankoff.so
binarysankoff_so_LDFLAGS = -module -avoid-version -shared


binarysankoff:	
	gcc -lz binarysankoff.c -o binarysankoff

NCD:
	gcc -lz NCD.c -o NCD
	
osx:
	gcc -dynamiclib -Wall -I/usr/include/python2.7/ -lpython2.7 -lz -o binarysankoff_osx.dylib binarysankoff_osx.c 
	mv ./binarysankoff_osx.dylib ./binarysankoff_osx.so

linux:
	gcc -shared -I/usr/include/python2.7/ -lpython2.7 -lz -o binarysankoff_linux.so binarysankoff_linux.c
	
	
