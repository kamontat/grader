from django.conf import settings
from pystalkd.Beanstalkd import Connection, SocketError

try:
	beanstalk = Connection(*settings.BEANSTALK)
except SocketError:
	beanstalk = None
