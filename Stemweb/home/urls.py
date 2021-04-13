from django.conf.urls import url
from .views import home, server_error, script_failure

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^home', home, name='stemweb_home_url'),
    url(r'^server_error', server_error, name='stemweb_server_error_url'),
    url(r'^script_failure', script_failure, name='stemweb_script_failure_url' ),
    url(r'^$', home),
]
