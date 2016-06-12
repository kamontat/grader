from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^task$', TaskAPI.as_view()),
]
