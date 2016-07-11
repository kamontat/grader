"""grader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.staticfiles.templatetags.staticfiles import static

def redirect_frontend(req):
    return redirect(static('frontend/index.html'))

urlpatterns = [
    url(r'^server/admin/', admin.site.urls),
    url(r'^server/', include('authapi.urls')),
    url(r'^server/', include('problems.urls')),
    url(r'^server/', include('submission.urls')),
    url(r'^server/codeload/', include('codeload.urls')),
    url(r'^server/', include('taskapi.urls')),
    url(r'^server/queue/', include('queuestats.urls')),
    url(r'^$', redirect_frontend),
]
