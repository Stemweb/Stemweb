from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from views import details, base, upload

urlpatterns = patterns('',
    url(r'^(?P<file_id>\d+)/$', details, name='files_details_url'),
    url(r'^base', base, name='files_base_url'),
    url(r'^upload', upload, name='files_upload_url'),
)
