from django.conf.urls.defaults import patterns, url
from views import details, base, upload

urlpatterns = patterns('',
    url(r'^(?P<file_id>\d+)/$', details, name='files_details_url'),
    url(r'^base', base, name='files_base_url'),
    url(r'^upload', upload, name='files_upload_url'),
)
