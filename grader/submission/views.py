import json

from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import NotFound, PermissionDenied, APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from problems.models import Test, Problem
from grader.beanstalk import beanstalk
from .serializers import *

class ResultsViewSet(ReadOnlyModelViewSet):
	serializer_class = ResultSerializer

	def get_queryset(self):
		return Result.objects.filter(
			problem_id=self.kwargs['problem_id'],
			user=self.request.user,
		)

class Submit(APIView):
	permission_classes = (IsAuthenticated,)

	def post(self, request, id, problem_id):
		if not beanstalk:
			raise QueueDown()

		try:
			problem = Problem.objects.get(pk=problem_id, test_id=id)
		except Problem.DoesNotExist:
			raise NotFound

		if not problem.is_visible() and not self.request.user.has_perm('change_problem'):
			raise NotFound

		if not self.is_problem_allow_submission(problem):
			raise PermissionDenied

		config = problem.get_graders()
		if not self.is_problem_ready(problem):
			raise ProblemNotReady

		if request.data['lang'] not in config['allowed']:
			raise ValidationError('Language is not allowed for submission')

		result = Result(
			problem = problem,
			user = request.user,
			state = 0,
			correct = None,
			code = request.data['code'],
			lang = request.data['lang'],
			count_stats = self.is_counting_stats()
		)
		result.save()

		result.create_job()

		return Response({
			success: True,
			id: result.id,
		})

	def is_problem_allow_submission(self, problem):
		return not problem.test.is_readonly() or self.request.user.has_perm('change_problem')

	def is_problem_ready(self, problem):
		config = problem.get_graders()
		# FIXME: Flip the condition
		if config == {} or not problem.input or (not problem.output and problem.comparator == 'hash'):
			return False
		return True

	def is_counting_stats(self, problem):
		"""Return true when user never have any correct submission"""
		return not Result.objects.filter(user=self.request.user, correct=1, problem=problem).exists()


class ProblemNotReady(APIException):
	status_code = 503
	default_detail = 'Problem is not ready for submission'

class QueueDown(APIException):
	status_code = 500
	default_detail = 'Queue server is down'
