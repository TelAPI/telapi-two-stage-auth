from django.conf.urls.defaults import patterns, include, url
from two_stage_auth import views


urlpatterns = patterns(
    'two_stage_auth.views',
    url(r'^user/$', views.user_page, name="user_page"),
    url(r'^token/$', views.generate_token, name="generate_token"),
    url(r'^login/$', views.login_page, name='login'),
    url(r'^logout/$', views.logout_page, name='logout'),
    url(r'^telml/call/(?P<username>.*?)/(?P<token>.*?)/$', views.telml_call, name='telml_call')
)
