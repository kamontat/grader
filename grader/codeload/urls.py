from django.conf.urls import url, include

from .views import *

urlpatterns = [
	url(r'^sub/(?P<id>[0-9]+)', load_submission),
	url(r'^input/(?P<id>[0-9]+)', load_input),
	url(r'^output/(?P<id>[0-9]+)', load_output),
]
