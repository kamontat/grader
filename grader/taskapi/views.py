from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, AuthenticationFailed

from submission.models import Result

class TaskAPI(APIView):
	def post(self, request):
		if not settings.WORKER_SHARED_SECRET:
			raise ImproperlyConfigured('WORKER_SHARED_SECRET is not configured')

		if settings.WORKER_SHARED_SECRET != request.data['key']:
			raise AuthenticationFailed('Incorrect shared secret')

		try:
			result = Result.objects.get(pk=request.data['result_id'])
		except Result.DoesNotExist:
			raise NotFound('Result not found')

		if request.data['correct']:
			result.state = 2
			result.correct = request.data['correct']
			result.result = request.data['result']
			result.error = request.data.get('error', '')

			if not result.error:
				result.error = request.data.get('compile', '')

			if not result.error:
				result.error = None
		else:
			result.state = 1

		result.save()

		return Response({
			'success': True
		})
