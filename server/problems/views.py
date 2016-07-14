from django.db.models import Q, Count
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *

class TestViewSet(viewsets.ModelViewSet):
	permission_classes = (IsAuthenticated,)
	serializer_class = TestSerializer

	def get_queryset(self):
		objects = Test.objects.all().annotate(problems=Count('problem'))

		if not self.request.user.has_perm('problems.change_test'):
			objects = objects.filter(Q(start__lte=timezone.now()) | Q(start=None))

		return objects

class ProblemViewSet(viewsets.ModelViewSet):
	permission_classes = (IsAuthenticated,)
	serializer_class = ProblemSerializer

	def get_queryset(self):
		objects = Problem.objects.filter(
			test_id=self.kwargs['test_pk'],
		)

		if not self.request.user.has_perm('problems.change_test'):
			objects = objects.filter(Q(test__start__lte=timezone.now()) | Q(test__start=None))

		return objects
