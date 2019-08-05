from django.conf.urls import url
from views import details, base, upload

urlpatterns = [
    url(r'^(?P<file_id>\d+)/$', details, name='files_details_url'),
    url(r'^base', base, name='files_base_url'),
    url(r'^upload', upload, name='files_upload_url')
]
