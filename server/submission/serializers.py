from django.contrib.auth.models import User

from rest_framework import serializers

from problems.models import Problem
from .models import *

class ResultSerializer(serializers.ModelSerializer):
	problem_id = serializers.PrimaryKeyRelatedField(source='problem', queryset=Problem.objects.all())
	user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all())
	has_code = serializers.SerializerMethodField()

	def get_has_code(self, object):
		return bool(object.code)

	class Meta:
		model = Result
		fields = (
			'id', 'problem_id', 'user_id', 'state', 'correct', 'result', 'lang',
			'error', 'created_at', 'updated_at', 'has_code',
		)
