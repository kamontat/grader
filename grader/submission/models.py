from django.db import models
from django.contrib.auth.models import User

class Result(models.Model):
	problem = models.ForeignKey('problems.Problem')
	user = models.ForeignKey(User)
	state = models.IntegerField(default=0, choices=[
		(0, 'Created'),
		(1, 'Grading'),
		(2, 'Graded'),
	])
	correct = models.IntegerField(null=True, blank=True, choices=[
		(None, 'Not graded'),
		(0, 'Incorrect'),
		(1, 'Correct'),
		(2, 'Error')
	])
	result = models.TextField(null=True, blank=True)
	code = models.TextField()
	lang = models.CharField(max_length=10)
	error = models.TextField(null=True, blank=True, default=None)
	count_stats = models.BooleanField(default=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		index_together = [
			['id', 'state', 'correct', 'count_stats'],
			['user', 'state', 'correct', 'problem']
		]

	def __str__(self):
		return 'Submission {} to problem {} by {}'.format(
			self.id,
			self.problem.name,
			self.user.username
		)
