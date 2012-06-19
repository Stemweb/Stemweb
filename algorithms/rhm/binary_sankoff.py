'''
Created on Apr 20, 2012

@author: slinkola
'''
import os
import sys
from time import sleep
import logging
from Stemweb.algorithms.tasks import AlgorithmTask

import binarysankoff

class RHM(AlgorithmTask):
	
	def __init_run__(self, *args, **kwargs):
		AlgorithmTask.__init_run__(self, *args, **kwargs)
		if self.algorithm_run:
			self.algorithm_run.image = os.path.join(self.run_args['url_base'], 'rhm.svg')
			self.algorithm_run.newick = os.path.join(self.run_args['url_base'], 'rhm_0.tre')
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
		