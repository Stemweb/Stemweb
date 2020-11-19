
import os
import time
import shutil
import logging
import datetime

from django.conf import settings
from models import AlgorithmRun

def remove_old_results_fs():
    """ removes results in file system (result files and result directories) which are older than settings.KEEP_RESULTS_DAYS """
    numdays = 60*60*24*int(settings.KEEP_RESULTS_DAYS)
    now = time.time()
    directory=os.path.join(settings.MEDIA_ROOT,"results/runs")
    logger = logging.getLogger('stemweb.algorithm_run')

    for root, dirs, files in os.walk(directory):
        for d in dirs:
            timestamp = os.path.getmtime(os.path.join(root,d))
            if now-numdays > timestamp:
                try:
                    logger.info('older results than %s days found in file system: removing %s ' % (settings.KEEP_RESULTS_DAYS, os.path.join(root,d)))
                    shutil.rmtree(os.path.join(root,d)) 
                except Exception,e:
                    #print e
                    logger.error('removing failed with error %s: ' % (e), exc_info=1)
                    pass
                else: 
                    logger.info('successfully removed')

def remove_old_results_db():
    """ removes metadata of results in the database where the end time of the runs are older than settings.KEEP_RESULTS_DAYS.
        The django based db access method models.AlgorithmRun.delete() is used
        With the models.py/delete()-method also the associated folders/subfolders/files are deleted
    """

    todaysDate = datetime.date.today()
    no_of_days = datetime.timedelta(days = int(settings.KEEP_RESULTS_DAYS)) 
    reference_date = todaysDate - no_of_days
    candidates = AlgorithmRun.objects.filter(end_time__lt=reference_date)
    print "################ candidates to delete ###################"
    for run in candidates:
        run.delete()
        #  logging about deletion is done by utils! It writes the executed SQL statement, e.g.:
        # stemweb_py27_1  | DEBUG 2020-11-11 01:14:31,177 utils 742 140041788659456 (0.001) DELETE FROM `algorithms_algorithmrun` WHERE `algorithms_algorithmrun`.`id` IN (2); args=(2,)



    



