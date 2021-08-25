from distutils.core import setup, Extension
setup(name = 'adding', version = '1.0',  \
   ext_modules = [Extension('adding', ['addingmodule.c'], \
			extra_compile_args = ['-DCMAKE_BUILD_TYPE=Debug'])
	])			    
	### KEEP line with "DCMAKE_BUILD_TYPE=Debug" active ONLY for debugging purpose!
