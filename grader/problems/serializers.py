from rest_framework import serializers

from .models import *

class TestSerializer(serializers.ModelSerializer):
	acl_edit = serializers.SerializerMethodField('can_edit')
	problem = serializers.SerializerMethodField()
	score = serializers.SerializerMethodField('get_user_score')
	finished = serializers.SerializerMethodField('get_user_finished')
	start = serializers.DateTimeField('')

	def can_edit(self, object):
		return self.context['request'].user.has_perm('problems.change_test', object)

	def get_problem(self, object):
		return object.problem_set.count()

	def get_user_score(self, object):
		if not self.context['request'].user.is_authenticated():
			return None

		return 1

	def get_user_finished(self, object):
		if not self.context['request'].user.is_authenticated():
			return None

		return 1

	class Meta:
		model = Test
		fields = (
			'id', 'name', 'mode', 'start', 'end', 'readonly', 'acl_edit',
			'problem', 'score', 'finished',
		)
