binarysankoff:	
	gcc -lz binarysankoff.c -o binarysankoff

NCD:
	gcc -lz NCD.c -o NCD
	
binarysankoff_python_osx:
	gcc -dynamiclib -I/usr/include/python2.7/ -lpython2.7 -lz -o binarysankoff.dylib binarysankoff_python.c 
	@echo -----------------------------------------------------------------
	@echo Remember to rename "binarysankoff.dylib" into "binarysankoff.so"!

binarysankoff_python:
	gcc -shared -I/usr/include/python2.7/ -lpython2.7 -lz -o binarysankoff.so binarysankoff_python.c
	
	
