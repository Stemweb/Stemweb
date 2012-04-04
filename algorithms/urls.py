from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from views import base

urlpatterns = patterns('',
    url(r'^base', base, name='algorithms_base_url'),

)