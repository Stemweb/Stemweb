pkglib_LTLIBRARIES = binarysankoff.so
binarysankoff_so_LDFLAGS = -module -avoid-version -shared


binarysankoff:	
	gcc -lz binarysankoff.c -o binarysankoff

NCD:
	gcc -lz NCD.c -o NCD
	
osx:
	gcc -dynamiclib -Wall -I/usr/include/python3.7/ -lpython3.7 -lz -o binarysankoff_osx.dylib binarysankoff_osx.c 
	mv ./binarysankoff_osx.dylib ./binarysankoff.so

linux37:	
	gcc -I/usr/include/python3.7/ -lpython3.7 -I/usr/include -L/usr/lib -fPIC -g -Wall -c binarysankoff_linux.c
	gcc -shared -fPIC -Wall -I/usr/include -L/usr/lib binarysankoff_linux.o -o binarysankoff.so -lz

linux38:	
	gcc -I/usr/include/python3.8/ -lpython3.8 -I/usr/include -L/usr/lib -fPIC -g -Wall -c binarysankoff_linux.c
	gcc -shared -fPIC -Wall -I/usr/include -L/usr/lib binarysankoff_linux.o -o binarysankoff.so -lz

linux39:	
	gcc -I/usr/include/python3.9/ -lpython3.9 -I/usr/include -L/usr/lib -fPIC -g -Wall -c binarysankoff_linux.c
	gcc -shared -fPIC -Wall -I/usr/include -L/usr/lib binarysankoff_linux.o -o binarysankoff.so -lz
