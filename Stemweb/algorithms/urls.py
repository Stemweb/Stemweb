from django.conf.urls.defaults import patterns, url
from views import base, details, delete_runs, run, results, available, process, jobstatus, processtest, testresponse

from .settings import ALGORITHM_URL_PREFIX as prefix

urlpatterns = patterns('',
    url(r'^%s/base/' % prefix, base, name = 'algorithms_base_url'),
    url(r'^%s/(?P<algo_id>\d+)/$' % prefix, details, name = 'algorithms_details_url'),
    url(r'^%s/delete/$' % prefix, delete_runs, name = 'algorithms_delete_runs_url'),
    url(r'^%s/run/(?P<algo_id>\d+)/$' % prefix, run, name = 'algorithms_run_algorithm_url'),
    url(r'^%s/results/(?P<run_id>\d+)/$' % prefix, results, name = 'algorithms_run_results_url'),
    
    # Following urls are for external algorithm runs.
    url(r'^%s/available/$' % prefix, available, name = 'algorithms_available_url'),
    url(r'^%s/process/(?P<algo_id>\d+)/$' % prefix, process, name = 'algorithms_process_url'),
    url(r'^%s/jobstatus/(?P<run_id>\d+)/$' % prefix, jobstatus, name = 'algorithms_jobstatus_url'),
    
    # Test URL
    url(r'^%s/processtest/$' % prefix, processtest, name = 'algorithms_test_url'),
    url(r'^%s/testresponse/$' % prefix, testresponse, name = 'algorithms_testresponse_url'),
)
