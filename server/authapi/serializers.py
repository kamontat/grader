from django.contrib.auth.models import User

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
	user = serializers.CharField(source='username', read_only=True)
	admin = serializers.SerializerMethodField('is_admin')

	def is_admin(self, user):
		return user.has_perm('problems.add_test')

	class Meta:
		model = User
		fields = ('id', 'user', 'admin')
