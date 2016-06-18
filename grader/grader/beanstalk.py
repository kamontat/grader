from django.conf import settings
from pystalkd.Beanstalkd import Connection, SocketError

try:
	beanstalk = Connection(*settings.BEANSTALK)
	beanstalk.use(settings.BEANSTALK_TUBE)
except SocketError:
	beanstalk = None
