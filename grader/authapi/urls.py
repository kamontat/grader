from django.conf.urls import url, include
from .views import *

urlpatterns = [
	url(r'^auth_password/$', Login.as_view()),
	url(r'^auth_password/register$', Register.as_view()),

	url(r'^user$', UserView.as_view()),
	url(r'^logout', api_logout),

    url(r'^auth_password/api-auth/', include('rest_framework.urls'))
]
