import yaml

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from .storage import *
from .validators import *

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

def input_filename(instance, filename):
	return 'input/{}'.format(instance.id)
def output_filename(instance, filename):
	return 'output/{}'.format(instance.id)

class Problem(models.Model):
	test = models.ForeignKey(Test)
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True, help_text='<a href="http://commonmark.org/help/">Markdown</a> and full HTML allowed')
	point = models.IntegerField(default=1)
	creator = models.CharField(max_length=255, blank=True, default='', help_text='Any text is OK')
	graders = models.TextField(
		blank=True, default='time_limit: 1\nmemory_limit: 64\nallowed:\n- java',
		verbose_name='Grader configuration',
		help_text='Allowed are list of file extensions, not language name. Must be valid YAML',
		validators=[validate_grader_schema]
	)

	input_lang = models.CharField(max_length=10, null=True, blank=True,
		verbose_name='Input generator language', choices=[
			('py', 'Python 2'),
			('py3', 'Python 3'),
		])
	input = models.FileField(upload_to=input_filename, null=True, blank=True, verbose_name='Input generator source', storage=CodeloadFileSystemStorage('input'))

	output_lang = models.CharField(max_length=10, null=True, blank=True,
		verbose_name='Solution language', choices=[
			('java', 'Java'),
			('py', 'Python'),
			('py3', 'Python 3'),
		])
	output = models.FileField(upload_to=output_filename, null=True, blank=True, verbose_name='Solution', storage=CodeloadFileSystemStorage('output'))

	comparator = models.CharField(max_length=10, default="hash", choices=[
		('hash', 'Grader'),
	], editable=False)

	def get_graders(self):
		try:
			data = yaml.safe_load(self.graders)
		except yaml.YAMLError:
			data = {}

		if type(data) != dict:
			data = {}

		if not self.input or (not self.output and self.comparator == 'hash'):
			data['invalid'] = True

		return data

	def __str__(self):
		return self.name

	def clean(self):
		if self.input and not self.input_lang:
			raise ValidationError({
				'input_lang': 'Required if {} is present'.format(self._meta.get_field('input').verbose_name)
			})
		if self.input_lang and not self.input:
			raise ValidationError({
				'input': 'Required if {} is present'.format(self._meta.get_field('input_lang').verbose_name)
			})
		if self.output and not self.output_lang:
			raise ValidationError({
				'output_lang': 'Required if {} is present'.format(self._meta.get_field('output').verbose_name)
			})
		if self.output_lang and not self.output:
			raise ValidationError({
				'output': 'Required if {} is present'.format(self._meta.get_field('output_lang').verbose_name)
			})

	class Meta:
		ordering = ['test', 'name']
