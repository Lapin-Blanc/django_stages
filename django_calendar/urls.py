from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', view=views.accueil, name='accueil'),
    url(r'^horaires/$', view=views.horaires, name='horaires'),

    url(r'^calendar_login/$', auth_views.login, kwargs={"template_name":"admin/login.html"}, name='calendar_login'),
    url(r'^calendar_logout/$', auth_views.logout, kwargs={"next_page":"../"}, name="calendar_logout"),
    # ajax requests
    url(r'^horaires/get_events/$', views.get_events, name='get_events'),
    url(r'^horaires/create_event/$', views.create_event, name='create_event'),
    url(r'^horaires/delete_event/$', views.delete_event, name='delete_event'),
    url(r'^horaires/move_event/$', views.move_event, name='move_event'),
    url(r'^horaires/resize_event/$', views.resize_event, name='resize_event'),
]
