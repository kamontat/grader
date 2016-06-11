from django.conf.urls import url, include

from rest_framework_nested import routers
from .views import *

router = routers.SimpleRouter()
router.register(r'test', TestViewSet, base_name='tests')

test_router = routers.NestedSimpleRouter(router, r'test', lookup='test')
test_router.register(r'problems', ProblemViewSet, base_name='problems')

urlpatterns = [
	url(r'^', include(router.urls)),
	url(r'^', include(test_router.urls)),
]
