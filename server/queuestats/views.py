from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from grader import beanstalk

class StatsAPI(APIView):
	permission_classes = (IsAdminUser,)

	def get(self, request):
		instance = beanstalk.get()
		if not instance:
			raise APIException('Queue server is not ready')

		stats = instance.stats()
		tube_stats = instance.stats_tube(instance.using())

		return Response({
			'stats': stats,
			'tube_stats': tube_stats,
		})
