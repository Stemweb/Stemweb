from . import settings
from django.conf.urls import include, url
from django.views import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', include('Stemweb.home.urls')),
    url(r'^files/', include('Stemweb.files.urls')),
    url(r'^', include('Stemweb.algorithms.urls')),
    url(r'^media/(?P<path>.*)$', static.serve,
        {'document_root': settings.MEDIA_ROOT},
        name='stemweb_media_root_url'),

    # These are the registration apps own urls. Check documentation for the usage.
    # https://bitbucket.org/ubernostrum/django-registration/src/tip/docs/quickstart.rst
    #(r'^accounts/', include('registration.backends.default.urls')),
    #url(r'^accounts/', include('Stemweb.third_party_apps.registration.backends.default.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
]
