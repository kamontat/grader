from django.contrib import admin
from django.conf import settings

from .models import *

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'name', 'start', 'end', 'readonly', 'problem_count',
	)
	list_editable = ('readonly',)
	list_filter = ('readonly',)
	search_fields = ('id', 'name',)
	list_display_links = ('id', 'name')

	def problem_count(self, object):
		return object.problem_set.count()
	problem_count.short_description = 'Problems'

	def view_on_site(self, obj):
		return '{}#/{}'.format(settings.FRONTEND_URL, obj.id)

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'test', 'name', 'point', 'creator',
		'input_lang', 'has_input', 'output_lang', 'has_output'
	)
	list_display_links = ('id', 'name')
	list_filter = ('test', 'input_lang', 'output_lang', 'point')
	search_fields = ('name',)

	fieldsets = (
		(None, {
			'fields': ('test', 'name', 'description', 'point', 'creator')
		}),
		('Input generator', {
			'fields': ('input', 'input_lang')
		}),
		('Solution', {
			'fields': ('output', 'output_lang')
		}),
		('Advanced', {
			'classes': ('collapse',),
			'fields': ('graders',)
		}),
	)

	def has_input(self, object):
		return bool(object.input)
	has_input.boolean = True

	def has_output(self, object):
		return bool(object.output)
	has_output.boolean = True

	def view_on_site(self, obj):
		return '{}#/{}/{}'.format(settings.FRONTEND_URL, obj.test.id, obj.id)
