from .models import Problem
import json
from urllib.request import urlopen
from .models import Problem
from random import randint
from datetime import datetime, timedelta
from django.utils import timezone
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
import math

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
    try:
        URL = "https://codeforces.com/api/user.info?handles=" + handle
        response = urlopen(URL)
        response_data = json.loads(response.read())
        return response_data["status"] == "OK"
    except:
        return False


def submission_to_problem(submission):
    return str(submission["contestId"]) + submission["problem"]["index"]


def rating_color(rating):
    if rating < 1200:
        return ("gray", "#ebedf0")

    elif rating < 1400:
        return ("green", "#e9f5ea")

    elif rating < 1600:
        return ("cyan", "#e6f7f6")

    elif rating < 1900:
        return ("#0700c4", "#e8ecfa")

    elif rating < 2100:
        return ("#a100c2", "#eee1f7")

    elif rating < 2300:
        return ("#ffea00", "#ffffeb")

    elif rating < 2400:
        return ("#ed8b00", "#f7eddf")

    elif rating < 2600:
        return ("#fc5b00", "#ffe8db")

    elif rating < 3000:
        return ("#ff1500", "#fcb7b1")

    else:
        return ("#5e010f", "#deb8be")


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
        
        if rproblem is None:
            continue

        color, bg_color = rating_color(rproblem.rating)

        res.append((rproblem, color, bg_color))

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


def apply_rating_change(profile, delta, direct_apply=False):
    profile.virtual_rating += delta

    if direct_apply:
        profile.virtual_rating = delta

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

    contest_id, index = parse_problem_id(profile.current_problem)
    contest_id = int(contest_id)

    problem = Problem.objects.get(contest_id=contest_id, index=index)

    if timezone.now() > profile.deadline:        
        delta = 0

        if validate_result:
            delta = rating_gain(profile.virtual_rating, problem.rating)

        else:
            delta = rating_loss(profile.virtual_rating, problem.rating)

        apply_rating_change(profile, delta)
        return True

    elif validate_result:
        delta = rating_gain(profile.virtual_rating, problem.rating)
        apply_rating_change(profile, delta)
        return True

    else:
        return False


def rating_gain(user_rating, problem_rating, magnitude=10):
    chance = 1 / (1 + 10 ** ((problem_rating - user_rating) / 500))
    return min(magnitude * 10, int(math.floor(magnitude * (0.5 / chance))))


def rating_loss(user_rating, problem_rating, magnitude=10):
    chance = 1 / (1 + 10 ** ((problem_rating - user_rating) / 500))
    chance = 1 - chance
    return max(- int(math.floor(magnitude * (0.5 / chance))), magnitude * -10)


def make_graph(y):
    fig = plt.figure()
    fig.set_size_inches(12.5, 5.5)
    x = range(len(y))
    max_y = max(y)
    max_y = max_y + 200 - max_y % 100
    min_y = min(y)
    min_y = min_y - 100 - min_y % 100
    print(max_y)
    plt.ylim(min_y, max_y)
    plt.xlim(0, len(y) - 1)

    cp = [0, 1200, 1400, 1600, 1900, 2100, 2300, 2400, 2600, 3000, 3600]

    for i in range(10):
        cl, bcl = rating_color(cp[i])
        plt.axhspan(cp[i], cp[i + 1], color=bcl)

    plt.plot(x, y)
    imgdata = StringIO()
    fig.savefig(imgdata, format="svg")
    # imgdata.seek(0)

    data = imgdata.getvalue()
    return data


def reset_rating_progress(profile):
    progress = eval(profile.rating_progress)
    progress = [progress[-1]]

    profile.rating_progress = repr(progress)
    profile.save()

def give_up_problem(profile):
    contest_id, index = parse_problem_id(profile.current_problem)
    contest_id = int(contest_id)

    problem = Problem.objects.get(contest_id=contest_id, index=index)
    delta = rating_loss(profile.virtual_rating, problem.rating)

    apply_rating_change(profile, delta)
