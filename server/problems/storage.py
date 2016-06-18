from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.apps import apps

class CodeloadFileSystemStorage(FileSystemStorage):
	def __init__(self, type, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if type not in ('input', 'output'):
			raise ValueError('type must be input or output')

		self._type = type
		self._model = None

	def url(self, name):
		instance = self.get_instance(name)
		return reverse('load_{}'.format(self._type), args=[instance.id])

	def get_instance(self, name):
		if not self._model:
			self._model = apps.get_model('problems.problem')

		kwargs = {}
		kwargs[self._type] = name

		return self._model.objects.get(**kwargs)
