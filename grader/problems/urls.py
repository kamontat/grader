from rest_framework import routers
from .views import *

router = routers.SimpleRouter()
router.register(r'test', TestViewSet)
urlpatterns = router.urls
