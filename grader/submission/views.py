from collections import namedtuple

from django.db import connection

from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from problems.models import Test
from .serializers import *

StatsTuple = namedtuple('StatsTuple', ['id', 'attempt', 'passed'])
ScoreboardUserTuple = namedtuple('ScoreboardUserTuple', ['id', 'username', 'score'])
ScoreboardProblemTuple = namedtuple('ScoreboardProblemTuple', ['problem_id', 'id', 'name', 'lang', 'created_at', 'correct', 'size', 'wrong'])

class Stats(APIView):
	permission_classes = (AllowAny,)

	def get(self, request, id):
		try:
			test = Test.objects.get(pk=id)
		except Test.DoesNotExist:
			raise NotFound

		cursor = connection.cursor()
		cursor.execute("""SELECT `problems_problem`.`id` AS `id`,
			(
				SELECT COUNT(*)
				FROM `submission_result`
				WHERE `problems_problem`.`id` = `submission_result`.`problem_id`
				AND `submission_result`.`state` = 2
				AND `submission_result`.`correct` IS NOT NULL
				AND `submission_result`.`count_stats` = 1
			) AS `attempt`,
			(
				SELECT COUNT(*)
				FROM `submission_result`
				WHERE `problems_problem`.`id` = `submission_result`.`problem_id`
				AND `submission_result`.`state` = 2
				AND `submission_result`.`correct` = 1
				AND `submission_result`.`count_stats` = 1
			) AS `passed`
			FROM `problems_problem`
			WHERE `problems_problem`.`test_id` = %s""", [test.id])

		out = []

		for item in cursor:
			item = StatsTuple(*item)
			out.append(item._asdict())

		return Response(out)

class Scoreboard(APIView):
	permission_classes = (AllowAny,)

	def get(self, request, id):
		if not request.user.has_perm('problems.change_test'):
			raise PermissionDenied('User require change_test permission')

		try:
			test = Test.objects.get(pk=id)
		except Test.DoesNotExist:
			raise NotFound

		cursor = connection.cursor()
		cursor.execute("""SELECT `id`, `username`, CAST(SUM(CASE WHEN `correct` = 1 THEN `point` ELSE 0 END) AS int) AS score FROM (
			SELECT DISTINCT `problem_id`+" "+`user_id`, `auth_user`.`id`, `username`, `problems_problem`.`point`, `correct`
			FROM `submission_result`
			INNER JOIN `problems_problem` ON `problems_problem`.`id` = `submission_result`.`problem_id`
			INNER JOIN `auth_user` ON `submission_result`.`user_id` = `auth_user`.`id`
			WHERE `state` = 2
			AND `problems_problem`.`test_id` = %s
		) result
		GROUP BY `username`
		ORDER BY `score` DESC""", [test.id])

		out = []

		for user in cursor:
			user = ScoreboardUserTuple(*user)
			user_cursor = connection.cursor()
			user_cursor.execute("""SELECT DISTINCT `submission_result`.`problem_id`, `submission_result`.`id`, `problems_problem`.`name`, `submission_result`.`lang`, `submission_result`.`created_at`, `submission_result`.`correct`,
				LENGTH(`submission_result`.`code`) AS `size`,
			(
				SELECT COUNT(*) `wrong`
				FROM `submission_result` `r`
				WHERE `r`.`problem_id` = `submission_result`.`problem_id`
				AND `r`.`state` = 2 AND `r`.`correct` != 1
				AND `r`.`user_id` = `submission_result`.`user_id`
				AND `submission_result`.`count_stats` = 1
			) AS `wrong` FROM `submission_result`
			INNER JOIN `problems_problem` ON `problems_problem`.`id` = `submission_result`.`problem_id`
			WHERE `submission_result`.`state` = 2
			AND `submission_result`.`user_id` = %s
			AND `problems_problem`.`test_id` = %s
			ORDER BY (CASE WHEN `submission_result`.`correct` = 1 THEN 1 ELSE 0 END) ASC, `size` DESC, `id` ASC""", [user[0], test.id])

			problems = {}

			for problem in user_cursor:
				problem = ScoreboardProblemTuple(*problem)
				problem_dict = problem._asdict()

				if problem.correct != 1:
					del problem_dict['id']
					del problem_dict['lang']
					del problem_dict['size']

				# del id to prevent download

				problems[problem.problem_id] = problem_dict

			user_dict = user._asdict()
			user_dict['problems'] = problems
			out.append(user_dict)

		return Response(out)
