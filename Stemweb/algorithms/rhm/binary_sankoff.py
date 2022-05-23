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
import Stemweb.algorithms.settings
from Stemweb.algorithms.tasks import AlgorithmTask
from Stemweb._celery import celery_app
import binarysankoff
import subprocess
import shutil


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

		in_folder = run_args["infolder"] ### set in utils.build_external_args()   ### = path + filename 
		out_folder = run_args["outfolder"]
		i_max = run_args["imax"]

		file_dir = os.path.dirname(in_folder)
		name_without_ext = os.path.splitext(os.path.basename(in_folder))[0]
		multi_file_in_dir = os.path.join(file_dir, name_without_ext)
		#print('########## class RHM(AlgorithmTask): input path / multi_file_dir = ', multi_file_in_dir, '++++++++++++++++++++++++++')

		#print('####################  RHM: in_folder, multi_file_in_dir, out_folder, file_name, imax,  ',in_folder, '///', multi_file_in_dir, '///' ,out_folder, '///', file_name, '///', i_max , '++++++++\n' )

		# do the main rhm algorithm via c-extension: create the *.dot file:
		binarysankoff.py_main(strap, multi_file_in_dir , out_folder, file_name, i_max)
		
		# now do some folow up jobs via shell scripts
		# create the sankoff-tree.tre file (in the Newick tree format) by executing rhm.sh
		# note that also 'sed', 'awk' and 'neato' (from GraphViz) need to be installed as they are called in rhm.sh
		
		source1 = '/home/stemweb/Stemweb/algorithms/rhm/quartet2nexus.awk'
		source2 = '/home/stemweb/Stemweb/algorithms/rhm/rhm.sh'   # rhm.sh calls quartet2nexus.awk

		shutil.copy2(source1, out_folder)		# copy2 preserves metadata (like in shell command: cp -p src dst)
		shutil.copy2(source2, out_folder)

		binarysankoffresult_file_name = file_name + '_rhm.dot'
		shell_command = './rhm.sh' + ' ' + binarysankoffresult_file_name
		#print ('############## shell_command =', shell_command, '++++++++++++++++++++')

		os.chdir(out_folder)
		#subprocess.run(shell_command, shell = True, check = True)
		#subprocess.run(shell_command, shell = True)
		proc = subprocess.Popen(shell_command, shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdout, stderr) = proc.communicate()
		if stderr:
			#print ("\n############### rhm.sh script gave some error ############################\n")
			#print (type(stderr))
			#print ("\n\n")
			#print (stderr)
			#print ("\n###########################################\n")

			self.algorithm_run.error_msg = stderr
			self.algorithm_run.status = Stemweb.algorithms.settings.STATUS_CODES['failure']
			self.algorithm_run.save()

		# rename result files to target file-names:
		newick_file_name = file_name + '_rhm.tre'
		os.rename('sankoff-tree.tre', newick_file_name)
		noint_file_name = file_name + '_noint_rhm.dot'
		os.rename('sankoff-tree_noint.dot', noint_file_name)
		plot_file_name = file_name + '_rhm.pdf'
		os.rename('sankoff-tree.pdf', plot_file_name)
		### dot-result file name (file_name + '_rhm.dot') can be kept as it is

		#print('\n########## class RHM(AlgorithmTask): newick_path = ', self.newick_path, '++++++++++++++++++++++++++\n\n')
		#print('\n########## class RHM(AlgorithmTask): image_path = ', self.image_path, '++++++++++++++++++++++++++\n\n')
		from Stemweb.algorithms.utils import newick2img		### imported late because of error if done in import section
		newick2img(self.newick_path, self.image_path, radial = self.radial_image)

		# delete these 2 files in out_folder
		if os.path.exists("rhm.sh"):
			os.remove("rhm.sh")
		if os.path.exists("quartet2nexus.awk"):
			os.remove("quartet2nexus.awk")

		sleep(0.1)
		self._stop.value = 1

RHM = celery_app.register_task(RHM())
