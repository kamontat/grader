from docker import Client

class DockerRunner:
	def __init__(self, host):
		self.docker = Client(base_url=host)
