from django.core.management.base import BaseCommand
from django.db import connection
from django.core.files import File

from problems.models import *

class Command(BaseCommand):
	help = 'Migrate data from v1'

	def handle(self, *args, **options):
		cursor = connection.cursor()
		cursor.execute('INSERT INTO `problems_problem` (id, name, description, point, creator, graders, input_lang, output_lang, comparator, test_id) SELECT id, name, description, point, creator, graders, input_lang, output_lang, comparator, test_id FROM `problems`')
		cursor.execute('SELECT id, input, output FROM `problems`')

		for id, input, output in cursor:
			problem = Problem.objects.get(pk=id)
			if input and problem.input_lang:
				open('/tmp/migrate-tmp', 'w').write(input)
				fp = File(open('/tmp/migrate-tmp', 'r'))
				problem.input.save('input.{}'.format(problem.input_lang), fp, save=False)
				print('[{}] updated input {}'.format(problem.id, problem.input_lang))

			if output and problem.output_lang:
				open('/tmp/migrate-tmp', 'w').write(output)
				fp = File(open('/tmp/migrate-tmp', 'r'))
				problem.output.save('output.{}'.format(problem.output_lang), fp, save=False)
				print('[{}] updated output {}'.format(problem.id, problem.output_lang))

			problem.save()
