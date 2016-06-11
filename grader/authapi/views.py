from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, APIException, ParseError

from .serializers import *
from .exceptions import *

class Login(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		if 'username' not in request.data or 'password' not in request.data:
			raise ParseError('username and password is required')

		user = authenticate(username=request.data['username'], password=request.data['password'])
		if not user:
			raise AuthenticationFailed(detail='Unable to authenticate you')

		if not user.is_active:
			raise AuthenticationFailed(detail='User disabled')

		login(request, user)
		return Response(UserSerializer(user).data)


class Register(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		if not settings.REGISTER_ALLOWED:
			raise RegisterNotAvailable

		if 'username' not in request.data or 'password' not in request.data:
			raise ParseError('username and password is required')

		try:
			user = User.objects.create_user(request.data['username'], 'notrequired@example.com', request.data['password'])
			user.save()
		except IntegrityError:
			raise APIException('Unable to create user')

		return Response(UserSerializer(user).data)

class UserView(APIView):
	permission_classes = (AllowAny,)

	def get(self, request):
		if not request.user.is_authenticated():
			return Response({})

		return Response(UserSerializer(request.user).data)

def api_logout(request):
	logout(request)
	return redirect(settings.FRONTEND_URL)
