from django.conf.urls import url, include

from rest_framework import routers

from .views import *
from .stats import *

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'test/(?P<id>[0-9]+)/problems/(?P<problem_id>[0-9]+)/submissions', ResultsViewSet, base_name='result')

urlpatterns = [
	url(r'^test/(?P<id>[0-9]+)/stats', Stats.as_view()),
	url(r'^test/(?P<id>[0-9]+)/scoreboard', Scoreboard.as_view()),
	url(r'^test/(?P<id>[0-9]+)/problems/(?P<problem_id>[0-9]+)/submit', Submit.as_view()),
	url(r'', include(router.urls))
]
