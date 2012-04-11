from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from views import base, details, previous_runs, delete_runs, run, results

urlpatterns = patterns('',
    url(r'^base', base, name = 'algorithms_base_url'),
    url(r'^(?P<algo_id>\d+)/$', details, name = 'algorithms_details_url'),
    url(r'^runs/(?P<algo_id>\d+)/$', previous_runs, name = 'algorithms_previous_runs_url'),
    url(r'^delete/$', delete_runs, name = 'algorithms_delete_runs_url'),
    url(r'^run/(?P<algo_id>\d+)/$', run, name = 'algorithms_run_algorithm_url'),
    url(r'^results/(?P<run_id>\d+)/$', results, name = 'algorithms_run_results_url')
)