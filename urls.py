from django.conf.urls.defaults import patterns, include, url
import django_proto.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'django_proto.views.home', name='home'),
    # url(r'^django_proto/', include())
    # url(r'^$', 'Stemweb.views.home', name='home')
    # url(r'^Stemweb/', include('Stemweb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
