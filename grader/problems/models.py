import json

from django.db import models
from django.utils import timezone

class Test(models.Model):
	name = models.CharField(max_length=255)
	mode = models.CharField(max_length=15, default='practice', choices=[
		('practice', 'Practice'),
	], editable=False)
	start = models.DateTimeField(null=True, blank=True, help_text='Time to start this test. Users without permission will not see the test until this time')
	end = models.DateTimeField(null=True, blank=True, help_text='Time to end this test. Users without permission will be unable to submit solution')
	readonly = models.BooleanField(default=False, help_text='Disable submission. Users with permission will still able to submit solution regardless.')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def is_visible(self):
		if not self.start:
			return True

		return timezone.now() > self.start

	def is_readonly(self):
		if self.readonly:
			return self.readonly

		if not self.is_visible():
			return False

		if self.end:
			return timezone.now() > self.end

		return False

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class Problem(models.Model):
	test = models.ForeignKey(Test)
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	point = models.IntegerField(default=1)
	creator = models.CharField(max_length=255, blank=True, default='', help_text='Any text is OK')
	graders = models.TextField(
		blank=True, default='{"grader":{"time_limit":1,"memory_limit":64,"allowed":["java"]}}',
		verbose_name='Grader configuration',
		help_text='Allowed are list of file extensions, not language name. Must be valid JSON'
	)

	input_lang = models.CharField(max_length=10, null=True, blank=True,
		verbose_name='Input generator language', choices=[
			('py', 'Python 2'),
			('java', 'Java'),
			('php', 'PHP'),
		])
	input = models.FileField(upload_to='input', null=True, blank=True, verbose_name='Input generator source')

	output_lang = models.CharField(max_length=10, null=True, blank=True,
		verbose_name='Solution language', choices=[
			('c', 'C'),
			('cpp', 'C++'),
			('cs', 'C#'),
			('java', 'Java'),
			('js', 'JavaScript'),
			('php', 'PHP'),
			('py', 'Python'),
			('py3', 'Python 3'),
			('rb', 'Ruby'),
		])
	output = models.FileField(upload_to='output', null=True, blank=True, verbose_name='Solution')

	comparator = models.CharField(max_length=10, default="hash", choices=[
		('hash', 'Grader'),
	], editable=False)

	def get_graders(self):
		try:
			data = json.loads(self.graders)
		except json.decoder.JSONDecodeError:
			data = {}

		if type(data) != dict:
			data = {}

		if not self.input or (not self.output and self.comparator == 'hash'):
			data['invalid'] = True

		return data

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']
