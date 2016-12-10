import yaml
import cerberus

from django.core.exceptions import ValidationError

def validate_yaml(value):
	try:
		yaml.safe_load(value)
	except yaml.YAMLError:
		raise ValidationError('Data is not valid YAML')

schema = {
	'time_limit': {
		'type': 'integer',
		'min': 1,
	},
	'memory_limit': {
		'type': 'integer',
		'min': 32,
	},
	'allowed': {
		'required': True,
		'type': 'list',
		'schema': {
			'type': 'string',
			'regex': r'^(java|py|py3)$'
		}
	},
}

def validate_grader_schema(value):
	validate_yaml(value)
	data = yaml.safe_load(value)
	validator = cerberus.Validator(schema)
	if not validator.validate(data):
		message = []

		for key, value in validator.errors.items():
			for item in value:
				message.append('{}: {}'.format(key, item))

		raise ValidationError(', '.join(message))
