import json
import logging
import re
import importlib

__all__ = ['Job', 'RESULT', 'RUNNER']

RESULT = {
	'passed': 'P',
	'casing': 'C',
	'spacing': 'S',
	'failed': 'F',
	'error': 'E',
}

RUNNER = {
	'py': 'graderclient.runner.python.PythonRunner'
}

class Job:
	def ___init__(self, job):
		self.job = job
		self.logger = logging.getLogger('job-{}'.format(self.job_data['result_id']))

	def process(self):
		self.compile_input()
		self.compile_output()
		self.compile_submission()

		inputs = self.generate_input()
		result = []
		incorrect = False

		for item in inputs:
			output = self.run_output(item)
			solution = self.run_solution(item)
			compared = self.compare_result(output, solution)

			result.append(compared)
			if compared != RESULT['passed']:
				incorrect = True

		return {
			'correct': 'incorrect' if incorrect else 'correct',
			'result': ''.join(result),
		}

	def get_runner(self, language):
		try:
			logging.debug('Loading runner {} for {}', RUNNER[language], language)
			runner = RUNNER[language].split('.')
			module = importlib.import_module('.'.join(runner[:-1]))
			return getattr(module, runner[-1])
		except KeyError:
			raise UnknownRunnerException
		except Exception as e:
			raise RunnerException(e) from e

	def compile_input(self):
		pass

	def compile_output(self):
		pass

	def compile_submission(self):
		pass

	def run_output(self):
		pass

	def run_solution(self):
		pass

	def compare_result(self, a, b):
		a = a.strip()
		b = b.strip()
		# correct
		if a == b:
			return RESULT['passed']

		# incorrect spacing
		if re.sub(r'\s', '', a) == re.sub(r'\s', '', b):
			return RESULT['spacing']

		# incorrect casing
		if a.lower() == b.lower():
			return RESULT['casing']

		return RESULT['failed']

class UnknownRunnerException(KeyError):
	pass

class RunnerException(ImportError):
	pass
