import logging
import requests

__all__ = ['CORRECT', 'APIServer']

CORRECT = {
	'incorrect': 0,
	'correct': 1,
	'error': 2
}

class APIServer:
	def __init__(self, host, key):
		self.host = host
		self.key = key
		self.logger = logging.getLogger('api')

	def start_job(self, id):
		self.logger.info('Informing start of job %d', id)
		return self.api({
			'result_id': id,
		})

	def return_job(self, id, correct, result='', error=''):
		self.logger.info('Informing start of job %d', id)
		return self.api({
			'result_id': id,
			'correct': CORRECT[correct],
			'result': result,
			'error': error,
		})

	def api(self, data):
		data['key'] = self.key
		return requests.post(self.host, data=data).json()
