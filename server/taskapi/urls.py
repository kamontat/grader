from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^result$', TaskAPI.as_view()),
]
