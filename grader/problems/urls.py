from django.conf.urls import url, include

from rest_framework_nested import routers
from .views import *

router = routers.SimpleRouter()
router.register(r'test', TestViewSet)

test_router = routers.NestedSimpleRouter(router, r'test')
test_router.register(r'problems', ProblemViewSet)

urlpatterns = [
	url(r'^', include(router.urls)),
	url(r'^', include(test_router.urls)),
]
