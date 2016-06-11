import json

from django.db.models import Sum, Count

from rest_framework import serializers

from .models import *
from submission.models import Result

class TestSerializer(serializers.ModelSerializer):
	acl_edit = serializers.SerializerMethodField('can_edit')
	problem = serializers.SerializerMethodField()
	score = serializers.SerializerMethodField('get_user_score')
	finished = serializers.SerializerMethodField('get_user_finished')
	readonly = serializers.SerializerMethodField('is_readonly')
	start = serializers.DateTimeField('')

	def can_edit(self, object):
		return self.context['request'].user.has_perm('problems.change_test')

	def get_problem(self, object):
		return object.problem_set.count()

	def is_readonly(self, object):
		return object.is_readonly()

	def get_user_score(self, object):
		if not self.context['request'].user.is_authenticated():
			return None

		sum = Result.objects.filter(
			user=self.context['request'].user,
			state=2,
			correct=1,
			problem__test=object,
			count_stats=True
		).aggregate(Sum('problem__point'))['problem__point__sum']
		if not sum:
			sum = 0

		return sum

	def get_user_finished(self, object):
		if not self.context['request'].user.is_authenticated():
			return None

		return Result.objects.filter(
			user=self.context['request'].user,
			state=2,
			correct=1,
			problem__test=object,
			count_stats=True
		).count()

	class Meta:
		model = Test
		fields = (
			'id', 'name', 'mode', 'start', 'end', 'readonly', 'acl_edit',
			'problem', 'score', 'finished',
		)

class ProblemSerializer(serializers.ModelSerializer):
	acl_edit = serializers.SerializerMethodField('can_edit')
	graders = serializers.SerializerMethodField()
	passed = serializers.SerializerMethodField('get_user_passed')
	test_id = serializers.PrimaryKeyRelatedField(source='test', queryset=Test.objects.all())

	def can_edit(self, object):
		return self.context['request'].user.has_perm('problems.change_problem')

	def get_user_passed(self, object):
		if not self.context['request'].user.is_authenticated():
			return None

		return Result.objects.filter(
			user=self.context['request'].user,
			state=2,
			correct=1,
			problem=object
		).exists()

	def get_graders(self, object):
		out = object.get_graders()

		if not self.can_edit(object):
			for key in ('codejam', 'grader'):
				try:
					del out['key']
				except KeyError:
					pass

		return out

	class Meta:
		model = Problem
		fields = (
			'id', 'name', 'description', 'point', 'creator', 'graders',
			'test_id', 'acl_edit', 'input_lang', 'output_lang', 'comparator',
			'passed',
		)
