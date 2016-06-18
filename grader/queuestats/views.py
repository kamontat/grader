from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from grader.beanstalk import beanstalk

class StatsAPI(APIView):
	permission_classes = (IsAdminUser,)

	def get(self, request):
		if not beanstalk:
			raise APIException('Queue server is not ready')

		stats = beanstalk.stats()
		tube_stats = beanstalk.stats_tube(beanstalk.using())

		return Response({
			'stats': stats,
			'tube_stats': tube_stats,
		})
