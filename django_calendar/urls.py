from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', view=views.calendar_home, name='calendar_home'),
    url(r'^calendar_login/$', auth_views.login, kwargs={"template_name":"admin/login.html"}, name='calendar_login'),
    url(r'^calendar_logout/$', auth_views.logout, kwargs={"next_page":"../"}, name="calendar_logout"),
    url(r'^get_events/$', views.get_events, name='get_events'),
]
