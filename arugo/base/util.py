from .models import Problem
import json
from urllib.request import urlopen
from .models import Problem
from random import randint
from datetime import datetime, timedelta
from django.utils import timezone


def read_data(url):
    response = urlopen(url)
    response_data = json.loads(response.read())

    return response_data["result"]


def fetch_problemset():
    URL = "https://codeforces.com/api/problemset.problems"

    data = read_data(URL)
    problemset = data["problems"]

    for problem in problemset:
        if problem["type"] != "PROGRAMMING" or not "rating" in problem:
            continue
        p = Problem(
            contest_id=problem["contestId"],
            name=problem["name"],
            rating=problem["rating"],
            index=problem["index"],
        )
        p.save()


def get_latest_submissions(handle, cnt=500):
    cnt = min(cnt, 3000)
    URL = "https://codeforces.com/api/user.status?handle={}&from=1&cnt={}".format(
        handle, cnt
    )
    return read_data(URL)


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def validate_handle(handle):
    URL = "https://codeforces.com/api/user.info?handles=" + handle

    response = urlopen(URL)
    response_data = json.loads(response.read())

    return response_data["status"] == "OK"


def submission_to_problem(submission):
    return str(submission["contestId"]) + submission["problem"]["index"]


def get_challenge(handle, rating):
    latest_data = get_latest_submissions(handle, 2000)
    latest_data = filter(lambda submission: submission["verdict"] == "OK", latest_data)
    problem_id_only = set(map(submission_to_problem, latest_data))
    res = []

    for rt in rating:
        problemset = Problem.objects.filter(rating=rt)
        rproblem = None

        for iteration in range(20):
            problem = problemset[randint(0, len(problemset) - 1)]

            if str(problem.contest_id) + problem.index in problem_id_only:
                continue

            else:
                rproblem = problem
                break

        res.append(rproblem)

    return res


def validate_registration(handle):
    latest_data = get_latest_submissions(handle, 1)
    return (
        len(latest_data) > 0
        and latest_data[0]["verdict"] == "COMPILATION_ERROR"
        and latest_data[0]["problem"]["contestId"] == 1302
        and latest_data[0]["problem"]["index"] == "I"
    )


def validate_solution(handle, problem_id):
    latest_data = get_latest_submissions(handle, 1)
    return (
        latest_data[0]["verdict"] == "OK"
        and str(latest_data[0]["problem"]["contestId"])
        + latest_data[0]["problem"]["index"]
        == problem_id
    )


def accept_challenge(profile, contest_id, index):
    profile.in_progress = True
    profile.current_problem = str(contest_id) + index
    profile.deadline = timezone.now() + timedelta(hours=1, minutes=20)
    profile.save()


def parse_problem_id(problem_id):
    for i in range(len(problem_id)):
        if not problem_id[i].isdigit():
            return (problem_id[:i], problem_id[i:])


# def get_rating


def apply_rating_change(profile, delta):
    profile.virtual_rating += delta
    whole_rating = eval(profile.rating_progress)
    whole_rating.append(profile.virtual_rating)

    if len(whole_rating) > 30:
        whole_rating.pop(0)

    profile.rating_progress = repr(whole_rating)
    profile.in_progress = False
    profile.save()


def validate_challenge(profile):
    if not profile.in_progress:
        return False

    validate_result = validate_solution(profile.handle, profile.current_problem)

    if timezone.now() > profile.deadline:
        apply_rating_change(profile, 10 if validate_result else -10)
        return True

    elif validate_result:
        apply_rating_change(profile, 10)
        return True

    else:
        return False


# def rating_gain(user_rating, problem_rating, magnitude=10):
#     chance = 1 / (1 + 10 ** ((pr - rating) / 100))
#     sum = magnitude * 5

#     return []
