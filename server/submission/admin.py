from django.contrib import admin, messages
from .models import *

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'user', 'problem', 'state', 'correct', 'result',
		'lang', 'count_stats', 'created_at', 'updated_at'
	)
	list_filter = ('problem', 'state', 'lang', 'count_stats', 'user')
	search_fields = ('id', 'user__username')
	list_display_links = ('id', 'user', 'problem', 'state', 'correct')
	date_hierarchy = 'created_at'
	ordering = ['-updated_at']

	_model = None

	def get_readonly_fields(self, request, obj):
		allowed = ('count_stats',)
		return [f.name for f in Result._meta.get_fields() if f.name not in allowed]

	def rerun(self, request, queryset):
		for item in queryset:
			try:
				item.create_job()
			except AttributeError:
				messages.add_message(request, messages.ERROR, 'Cannot connect to the task queue')
				return
		queryset.update(state=0)
		messages.add_message(request, messages.SUCCESS, '{} items sent to task queue'.format(len(queryset)))

	rerun.short_description = 'Restart selected job'

	actions = [rerun]
