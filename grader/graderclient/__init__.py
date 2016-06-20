import json
import logging
import time
import threading
import traceback

import click
from pystalkd.Beanstalkd import Connection

from .job import Job, RESULT
from .server import APIServer

__all__ = ['main', 'beanstalk_connect', 'BeanstalkExtendThread']

FORMAT = '{asctime} {name} - {message}'
VERBOSE_LEVEL = [logging.INFO, logging.DEBUG]

@click.command()
@click.option('-b', '--beanstalk', default='127.0.0.1:11300', help='Beanstalkd server')
@click.option('-t', '--beanstalk-tube', default='grader', help='Beanstalkd tube name')
@click.option('-s', '--secret', envvar='GRADER_SECRET', required=True, help='Shared secret')
@click.option('--server', envvar='GRADER_SERVER', default='http://localhost/server/result', help='Grader result API URL')
@click.option('-v', '--verbose', count=1, help='Print job data and other details')
def main(**kwargs):
	"""Main command line of the application"""
	# Logging setup
	logging.basicConfig(format=FORMAT, style='{', level=VERBOSE_LEVEL[min(kwargs['verbose'], len(VERBOSE_LEVEL) - 1)])

	# Setup beanstalk
	beanstalk = beanstalk_connect(kwargs['beanstalk'], kwargs['beanstalk_tube'])

	# Setup server API
	server = APIServer(kwargs['server'], kwargs['secret'])

	while True:
		logging.info('Waiting for a job')
		# Get and parse a job
		job = beanstalk.reserve()
		job_data = json.loads(job.body)
		logging.info('Got a job')
		logging.debug('%s', job_data)

		# Inform the server
		server.start_job(job_data['result_id'])

		extender = BeanstalkExtendThread(job)
		extender.start()

		try:
			result = GraderJob(job_data).process()
			server.return_job(
				id=job_data['result_id'],
				**result,
			)
		except Exception as e:
			server.return_job(
				id=job_data['result_id'],
				correct='error',
				result=RESULT['error'],
				error=format_exception(e),
			)

		extender.stop()

def beanstalk_connect(host, tube):
	"""Setup beanstalk connection"""
	bs = host.split(':')
	beanstalk = Connection(bs[0], int(bs[1], 10))
	beanstalk.use(tube)
	return beanstalk

def format_exception(e):
	return ''.join(traceback.format_exception_only(type(e), e))

class BeanstalkExtendThread(threading.Thread):
	stopped = False

	def __init__(self, job, duration=10):
		super().__init__(self, name='beanstalkextend-{}'.format(job.job_id))
		self.job = job
		self.duration = duration

	def run(self):
		while True:
			time.sleep(self.duration)

			if self.stopped:
				return

			self.job.touch()

	def stop(self):
		self.stopped = True
