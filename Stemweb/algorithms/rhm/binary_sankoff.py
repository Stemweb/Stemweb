'''
Python wrapper for binary sankoff's C code.

@author: slinkola
'''
import os
import sys
from time import sleep
import logging
import platform
from Stemweb.algorithms.tasks import AlgorithmTask

#import binarysankoff	### temporarily deactivated; c-extension needs to be adopted for python3

class RHM(AlgorithmTask):
	name = "RHM"
	has_image = True
	has_newick = True
	has_networkx = False
	input_file_key = 'infolder'
	
	def __algorithm__(self, run_args = None):
		run_args['strap'] = 1
		run_args['file_name'] = self.input_file_name
		
		#binarysankoff.main(run_args)  ### temporarily deactivated
		
		from Stemweb.algorithms.utils import newick2img
		newick2img(self.newick_path, self.image_path, radial = self.radial_image)
		
		sleep(0.1)
		self._stop.value = 1
		
