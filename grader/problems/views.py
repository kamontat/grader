from rest_framework import viewsets

from .models import *
from .serializers import *

class TestViewSet(viewsets.ModelViewSet):
	queryset = Test.objects.all().order_by('name')
	serializer_class = TestSerializer

class ProblemViewSet(viewsets.ModelViewSet):
	serializer_class = ProblemSerializer

	def get_queryset(self):
		self.request

		return Problem.objects.filter(
			test_id=self.kwargs['test_pk']
		).order_by('name')
