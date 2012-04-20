'''
Created on Apr 20, 2012

@author: slinkola
'''
import os
import sys
from time import sleep
import logging
from Stemweb.algorithms.stoppable_algorithm import StoppableAlgorithm


import binarysankoff


class RHM(StoppableAlgorithm):
	
	
	def __init__(self, *args, **kwargs):
		StoppableAlgorithm.__init__(self, *args, **kwargs)
		self.algorithm_run.image = os.path.join(self.run_args['url_base'], 'rhm.svg')
		self.algorithm_run.save()
	
	def __algorithm__(self, run_args = None):
		run_args['strap'] = 1
		
		binarysankoff.main(run_args)
		nw_path = os.path.join(self.run_args['outfolder'], 'rhm_0.tre')
		svg_path = os.path.join(self.run_args['outfolder'], 'rhm.svg')
		
		
		from Stemweb.algorithms.utils import newick2svg
		newick2svg(nw_path, svg_path)
		
		sleep(0.1)
		self._stop.value = 1
		