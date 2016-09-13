from django.conf.urls import
urlpatterns = [
    url(r'^$', view=index, name='index'),
    url(r'^calendar/$', view=calendar_home, name='calendar_home'),
]
