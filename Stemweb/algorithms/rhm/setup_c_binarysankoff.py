from distutils.core import setup, Extension
setup(name = 'binarysankoff', version = '1.0',  \
	ext_modules = [Extension('binarysankoff', ['binarysankoff_linux.c'], \
			extra_link_args = ['-lz'], \
			extra_compile_args = ['-DCMAKE_BUILD_TYPE=Debug'])
	])			    
	### -lz is needed to get rid of ImportError "undefined symbol: gzclose" 
	### (though zlib.h is #included in binarysankoff_linux.c)
	### KEEP Debug- line active ONLY for debugging purpose!
