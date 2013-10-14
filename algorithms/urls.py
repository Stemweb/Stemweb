from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from views import base, details, delete_runs, run, results, available, process

from .settings import URL_PREFIX

urlpatterns = patterns('',
    url(r'^%s/base/' % URL_PREFIX, base, name = 'algorithms_base_url'),
    url(r'^%s/(?P<algo_id>\d+)/$' % URL_PREFIX, details, name = 'algorithms_details_url'),
    url(r'^%s/delete/$' % URL_PREFIX, delete_runs, name = 'algorithms_delete_runs_url'),
    url(r'^%s/run/(?P<algo_id>\d+)/$' % URL_PREFIX, run, name = 'algorithms_run_algorithm_url'),
    url(r'^%s/results/(?P<run_id>\d+)/$' % URL_PREFIX, results, name = 'algorithms_run_results_url'),
    
    # Following urls are for external algorithm runs.
    url(r'^%s/available/$' % URL_PREFIX, available, name = 'algorithms_available_url'),
    url(r'^%s/process/(?P<algo_id>\d+)/$' % URL_PREFIX, process, name = 'algorithms_process_url'),

)
