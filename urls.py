from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^home', 'django_proto.views.home', name='stemweb_home_url'),
    url(r'^upload', 'django_proto.views.upload', name='stemweb_upload_url'),
    url(r'^runparams/(?P<file_id>\d+)/$', 'django_proto.views.runparams', name='stemweb_runparams_url'),
    url(r'^run/(?P<file_id>\d+)/$', 'django_proto.views.run_script', name='stemweb_run_script_url'),
    url(r'^results/(?P<file_id>\d+)/(?P<run_id>\d+)/$', 'django_proto.views.results', name='stemweb_results_url'),
    url(r'^server_error', 'django_proto.views.server_error', name='stemweb_server_error_url'),
    url(r'^script_failure', 'django_proto.views.script_failure', name='stemweb_script_failure_url' ),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}, name='stemweb_media_root_url'),
    url(r'^base/', direct_to_template, {'template' : 'base.html'}),
    
    # These are the registration apps own urls. Check documentation for the usage.
    # https://bitbucket.org/ubernostrum/django-registration/src/tip/docs/quickstart.rst
    (r'^accounts/', include('registration.backends.default.urls')),
    
    (r'^files/', include('file_management.urls')),
    
    (r'^$', 'django_proto.views.home'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
