from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from views import base, details

urlpatterns = patterns('',
    url(r'^base', base, name = 'algorithms_base_url'),
    url(r'^(?P<algo_id>\d+)/$', details, name = 'algorithms_details_url'),

)