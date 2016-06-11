from django.conf.urls import url, include
from .views import *
from .stats import *

urlpatterns = [
	url(r'^test/(?P<id>[0-9]+)/stats', Stats.as_view()),
	url(r'^test/(?P<id>[0-9]+)/scoreboard', Scoreboard.as_view()),
	url(r'^test/(?P<id>[0-9]+)/problems/(?P<problem_id>[0-9]+)/submit', Submit.as_view()),
]
