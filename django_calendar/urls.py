from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', view=views.index, name='index'),
    url(r'^calendar/$', view=views.calendar_home, name='calendar_home'),
]
