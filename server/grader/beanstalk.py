import threading
from django.conf import settings
from pystalkd.Beanstalkd import Connection, SocketError

store = threading.local()

def get():
	try:
		return store.beanstalk
	except AttributeError:
		try:
			store.beanstalk = Connection(*settings.BEANSTALK)
			store.beanstalk.use(settings.BEANSTALK_TUBE)
		except SocketError:
			store.beanstalk = None
		
		return store.beanstalk
