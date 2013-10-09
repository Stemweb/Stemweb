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
	gcc -I/home/slinkola/test/stemenv/include/python2.6/ -lpython2.6 -I/home/slinkola/test/stemenv/include -L/home/slinkola/test/stemenv/lib -fPIC -g -Wall -c binarysankoff_linux.c
	gcc -shared -fPIC -Wall -I/home/slinkola/test/stemenv/include -L/home/slinkola/test/stemenv/lib \
	-Wl,-rpath,/home/slinkola/test/stemenv/lib -Wl,-soname,/home/slinkola/test/zlib-1.2.3.5/libz.so.1 \
	binarysankoff_linux.o -lz -o binarysankoff.so
	
	
