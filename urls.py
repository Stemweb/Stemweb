from django.conf.urls.defaults import patterns, url
import settings
#from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^home', 'django_proto.views.home'),
    url(r'^upload', 'django_proto.views.upload'),
    url(r'^runparams/(?P<file_id>\d+)/$', 'django_proto.views.runparams'),
    url(r'^run/(?P<file_id>\d+)/$', 'django_proto.views.run_script'),
    url(r'^results/(?P<file_id>\d+)/(?P<run_id>\d+)/$', 'django_proto.views.results'),
    url(r'^server_error', 'django_proto.views.server_error'),
    url(r'^script_failure', 'django_proto.views.script_failure'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
