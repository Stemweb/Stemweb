'''
Python wrapper for binary sankoff's C code.

@author: slinkola, 
	adapted for python3: pfugger
'''
import os
import sys
from time import sleep
import logging
import platform
from Stemweb.algorithms.tasks import AlgorithmTask
from Stemweb._celery import celery_app
import binarysankoff	

class RHM(AlgorithmTask):
	name = "RHM"
	has_image = True
	has_newick = True
	has_networkx = False
	input_file_key = 'infolder' ### NOT a dead code!!! used in task.py: class AlgorithmTask(Task).__init_run__

	
	def __algorithm__(self, run_args = None):
		strap = 1
		file_name = self.input_file_name

		#print('#################### iterate over run_args.items() ++++++++++++++++++++++++++++++\n' )
		#for item in run_args.items():
				#print('######### item = ', item)

		in_folder = run_args["infolder"] ### set in utils.build_external_args()
		out_folder = run_args["outfolder"]
		i_max = run_args["imax"]

		#print('####################  RHM: in_folder, out_folder, file_name, imax,  ',in_folder, '///' ,out_folder, '///', file_name, '///', i_max , '++++++++\n' )

		binarysankoff.py_main(strap, in_folder , out_folder, file_name, i_max) 

		from Stemweb.algorithms.utils import newick2img
		newick2img(self.newick_path, self.image_path, radial = self.radial_image)
		
		sleep(0.1)
		self._stop.value = 1

RHM = celery_app.register_task(RHM())
