from django.conf.urls.defaults import patterns, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^two_stage/', include('two_stage.urls')),
    )
