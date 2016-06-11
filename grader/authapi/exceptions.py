from rest_framework.exceptions import APIException

class RegisterNotAvailable(APIException):
	status_code = 503
	default_detail = 'Registration is disabled'
