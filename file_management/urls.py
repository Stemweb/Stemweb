from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template
from views import index, users_files, base

urlpatterns = patterns('',
    url(r'^index', index, name='file_management_index_url'),
    url(r'^users_files', users_files, name='file_management_users_files_url'),
    url(r'^base', base, name='file_management_base_url'),

)
