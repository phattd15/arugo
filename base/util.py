import json
import math
from datetime import timedelta
from io import StringIO
from random import randint
from urllib.request import urlopen

import matplotlib.pyplot as plt
import requests
from django.contrib.auth.models import User
from django.utils import timezone

from .models import AuthQuery, Profile
from .models import Problem, FetchData


def read_data(url):
    try:
        response = urlopen(url)
        response_data = []
        response_data = json.loads(response.read())

        if "result" in response_data:
            return response_data["result"]

        else:
            return []

    except:
        return []


def fetch_problemset():
    URL = "https://codeforces.com/api/problemset.problems"

    FetchData.objects.all().delete()
    Problem.objects.all().delete()

    fd = FetchData()
    fd.save()

    data = read_data(URL)

    if data == [] or not "problems" in data:
        return

    problemset = data["problems"]

    successful_saved = 0
    for problem in problemset:
        if (
                problem["type"] != "PROGRAMMING"
                or not "rating" in problem
                or "*special" in problem["tags"]
        ):
            continue

        if represents_int(problem["index"]):
            continue

        try:
            p = Problem(
                contest_id=problem["contestId"],
                name=problem["name"],
                rating=problem["rating"],
                index=problem["index"],
            )
            p.save()
            successful_saved += 1
            print(successful_saved)

        except:
            print("failed with ", problem)


def update_problemset():
    print("problemset updating")

    if len(AuthQuery.objects.all()) > 1000:
        AuthQuery.objects.all().delete()

    URL = "https://codeforces.com/api/problemset.problems"

    data = read_data(URL)

    if data == [] or not "problems" in data:
        return

    FetchData.objects.all().delete()
    fd = FetchData()
    fd.save()

    problemset = data["problems"]

    for problem in problemset[:30]:
        if (
                problem["type"] != "PROGRAMMING"
                or not "rating" in problem
                or "*special" in problem["tags"]
        ):
            continue

        if represents_int(problem["index"]):
            continue

        if Problem.objects.filter(
                contest_id=problem["contestId"], index=problem["index"]
        ):
            continue

        p = Problem(
            contest_id=problem["contestId"],
            name=problem["name"],
            rating=problem["rating"],
            index=problem["index"],
        )
        p.save()


def get_latest_submissions(handle, cnt=500):
    cnt = min(cnt, 8000)
    URL = "https://codeforces.com/api/user.status?handle={}&from=1&count={}".format(
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


# TODO: investigate this later. Bug caused by acmsguru.
def submission_to_problem(submission):
    try:
        str(submission["problem"]["contestId"]) + submission["problem"]["index"]

    except:
        print(submission)
        return "1000A"

    return str(submission["problem"]["contestId"]) + submission["problem"]["index"]


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


def get_challenge(handle, user_rating, rating):
    latest_data = get_latest_submissions(handle, 8000)
    latest_data = filter(
        lambda submission: "verdict" in submission and submission["verdict"] == "OK",
        latest_data,
    )
    problem_id_only = set(map(submission_to_problem, latest_data))
    res = []

    for rt in rating:
        problemset = Problem.objects.filter(rating=rt)

        if len(problemset) == 0:
            continue

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

        res.append(
            (
                rproblem,
                color,
                bg_color,
                rating_gain(user_rating, rt),
                rating_loss(user_rating, rt),
                color_rating_2(rt),
            )
        )

    return res


def safe_submission(submission):
    try:
        submission["verdict"]
        submission["problem"]["contestId"]
        submission["problem"]["index"]

    except:
        return False

    return True


def validate_solution(handle, problem_id, deadline):
    latest_data = get_latest_submissions(handle, 20)
    for submission in latest_data:
        if safe_submission(submission):
            if (
                    submission["creationTimeSeconds"] < deadline.timestamp()
                    and submission["verdict"] == "OK"
                    and str(submission["problem"]["contestId"])
                    + submission["problem"]["index"]
                    == problem_id
            ):
                return True

    return False


def accept_challenge(profile, contest_id, index):
    contest = Problem.objects.filter(
        contest_id=contest_id, index=index
    )

    if len(contest) == 0:
        return

    profile.in_progress = True
    profile.current_problem = str(contest[0].contest_id) + contest[0].index
    profile.deadline = timezone.now() + timedelta(hours=1, minutes=20)
    profile.save()


def parse_problem_id(problem_id):
    for i in range(len(problem_id)):
        if not problem_id[i].isdigit():
            return (problem_id[:i], problem_id[i:])


def apply_rating_change(profile, delta, problem, direct_apply=False):
    profile.msg = 1 if delta > 0 else 2
    profile.virtual_rating += delta

    if direct_apply:
        profile.virtual_rating = delta

    whole_rating = eval(profile.rating_progress)
    whole_rating.append(profile.virtual_rating)

    if len(whole_rating) > 150:
        whole_rating.pop(0)

    profile.rating_progress = repr(whole_rating)

    history = eval(profile.history)
    history.append((problem.contest_id, problem.index, delta))

    while len(history) > 25:
        history.pop(0)

    profile.history = repr(history)

    profile.in_progress = False
    profile.save()


def validate_challenge(profile):
    if not profile.in_progress:
        return False

    validate_result = validate_solution(
        profile.handle, profile.current_problem, profile.deadline
    )

    contest_id, index = parse_problem_id(profile.current_problem)
    contest_id = int(contest_id)

    problem = Problem.objects.get(
        contest_id=contest_id, index=index
    )

    if timezone.now() > profile.deadline:
        delta = 0

        if validate_result:
            delta = rating_gain(profile.virtual_rating, problem.rating)

        else:
            delta = rating_loss(profile.virtual_rating, problem.rating)

        apply_rating_change(profile, delta, problem)
        return True

    elif validate_result:
        delta = rating_gain(profile.virtual_rating, problem.rating)
        apply_rating_change(profile, delta, problem)
        return True

    else:
        return False


def rating_gain(user_rating, problem_rating, magnitude=16):
    if user_rating - problem_rating > 600:
        return 2
    elif user_rating - problem_rating > 1000:
        return 1

    chance = 1 / (1.15 + 10 ** ((problem_rating - user_rating) / 500))
    return min(magnitude * 8, int(math.floor(magnitude * (0.5 / chance))))


def rating_loss(user_rating, problem_rating, magnitude=16):
    chance = 1 / (1 + 10 ** ((problem_rating - user_rating) / 500))
    chance = 1 - chance
    return max(-int(math.floor(magnitude * (0.5 / chance))), magnitude * -8) + 1


def color_rating_2(rating):
    cp = [0, 1200, 1400, 1600, 1900, 2100, 2300, 2400, 2600, 3000, 4000]
    cl = [
        "#858585",
        "#7bc76d",
        "#6fc7c1",
        "#6e78c4",
        "#ad6eb8",
        "#aba84d",
        "#edab5a",
        "#ed5555",
        "#f50505",
        "#960000",
    ]

    for i in range(10):
        if rating < cp[i + 1]:
            return cl[i]


def make_graph(handle, y):
    fig = plt.figure()
    fig.set_size_inches(12.5, 5.5)
    x = range(len(y))
    max_y = max(y)
    max_y = max_y + 150
    min_y = min(y)
    min_y = min_y - 150
    plt.ylim(min_y, max_y)
    plt.xlim(0, len(y) - 1)

    cp = [0, 1200, 1400, 1600, 1900, 2100, 2300, 2400, 2600, 3000, 4000]
    cl = [
        "#858585",
        "#7bc76d",
        "#6fc7c1",
        "#6e78c4",
        "#ad6eb8",
        "#d1ce75",
        "#edab5a",
        "#ed5555",
        "#f50505",
        "#960000",
    ]
    for i in range(10):
        plt.axhspan(cp[i], cp[i + 1], color=cl[i])

    plt.title(handle + "'s rating progress chart")
    plt.plot(x, y, marker="o", color="#ffffff")
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

    problem = Problem.objects.get(
        contest_id=contest_id, index=index
    )
    delta = rating_loss(profile.virtual_rating, problem.rating)

    apply_rating_change(profile, delta, problem)


def can_be_parsed(s):
    try:
        progress = list(s.split())

        for rating in progress:
            if not represents_int(rating):
                return False

        return True

    except ValueError:
        return False


def update_progress(profile, s):
    if not can_be_parsed(s):
        return

    progress = list(map(int, s.split()))

    while len(progress) > 150:
        progress.pop()

    for i in range(len(progress)):
        if progress[i] > 4000:
            progress[i] = 4000

        if progress[i] < 0:
            progress[i] = 0

    profile.rating_progress = repr(progress)
    profile.virtual_rating = progress[-1]
    profile.save()


def remaining_time_convert(rem):
    rem = int(rem)
    rem = math.floor(rem)
    minutes = rem // 60
    seconds = rem % 60

    return (minutes, seconds)


def undergoing_auth_query(handle):
    query = AuthQuery.objects.filter(handle=handle)

    return len(query) > 0 and query[0].valid


def get_random_problem():
    id = randint(1, 7800)
    pp = Problem.objects.all()
    return pp[id]


def validate_auth_query(query):
    if not query.valid:
        return False

    latest_data = get_latest_submissions(query.handle, 1)

    if len(latest_data) == 0:
        return False

    sub_time = latest_data[0]["creationTimeSeconds"]

    if (
            len(latest_data) > 0
            and latest_data[0]["problem"]["contestId"] == query.contest_id
            and latest_data[0]["problem"]["index"] == query.index
    ):
        deadline = query.date + timedelta(minutes=2)
        if sub_time > query.date.timestamp() and sub_time < deadline.timestamp():
            query.valid = False

            user, profile = 1, 2

            if User.objects.filter(username=query.handle).exists():
                user = User.objects.get(username=query.handle)
                profile = Profile.objects.get(handle=query.handle)

            else:
                user = User.objects.create_user(
                    username=query.handle, password=query.password
                )
                user.save()
                profile = Profile(
                    user=user,
                    handle=query.handle,
                    virtual_rating=query.rating,
                    rating_progress="[]",
                )
                profile.save()

            user.password = query.password
            nxt_rating = eval(profile.rating_progress)
            nxt_rating.append(query.rating)
            profile.virtual_rating = query.rating
            profile.rating_progress = repr(nxt_rating)

            user.save()
            profile.save()
            query.save()

            return True

        return False

    return False


def discard_challenge(profile):
    profile.in_progress = False
    profile.save()


def update_username(username):
    url = 'https://codeforces.com/profile/' + username
    res = requests.get(url)
    res_url = res.url
    slash_pos = 0
    for i in range(len(res_url)):
        if res_url[i] == '/':
            slash_pos = i
    nxt_username = res_url[(slash_pos + 1):]
    # return nxt_username

    if nxt_username != username:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(handle=username)
        queries = AuthQuery.objects.filter(handle=username)

        if len(queries):
            queries.delete()

        profile.handle = nxt_username
        profile.save()

        user.username = nxt_username
        user.save()

        print("updated to " + nxt_username)

    return nxt_username
