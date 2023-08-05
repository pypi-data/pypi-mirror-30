from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^loadfiles/$', views.upload_files, name='upload_files'),
    url(r'^delete_select/$', views.delete_select, name='delete_select'),
    url(r'^move/$', views.move, name='move'),
    url(r'^(?P<classname>[\w-]+)/(?P<id>\d+)/delete$', views.delete_obj, name='delete_obj'),
]

