from django.http import HttpResponse, FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required

from problems.models import Problem
from submission.models import Result

mime = {
	'php': 'text/x-php',
	'py': 'text/x-python',
	'py3': 'text/x-python-3',
	'rb': 'text/x-ruby',
	'js': 'application/javascript',
	'java': 'text/x-java',
	'c': 'text/x-c',
	'cs': 'text/x-csharp',
	'cpp': 'text/x-c++',
	'java': 'text/x-java'
}

@login_required
def load_submission(request, id):
	submission = get_object_or_404(Result, pk=id)
	if submission.user != request.user:
		raise HttpResponseForbidden

	return HttpResponse(submission.code, content_type=mime.get(submission.lang, 'text/plain'))

@permission_required('problems.change_problem')
def load_input(request, id):
	problem = get_object_or_404(Problem, pk=id)
	return FileResponse(problem.input, content_type=mime.get(problem.input_lang, 'text/plain'))

@permission_required('problems.change_problem')
def load_output(request, id):
	problem = get_object_or_404(Problem, pk=id)
	return FileResponse(problem.output, content_type=mime.get(problem.output_lang, 'text/plain'))
