from .models import Problem
import json
from urllib.request import urlopen
from .models import Problem
from random import randint

def read_data(url):
    response = urlopen(url)
    response_data = json.loads(response.read())    

    return response_data['result']

def fetch_problemset():
    URL = 'https://codeforces.com/api/problemset.problems'

    data = read_data(URL)
    problemset = data['problems']

    for problem in problemset:
        if problem['type'] != 'PROGRAMMING' or not 'rating' in problem:
            continue
        p = Problem(contest_id=problem['contestId'], name=problem['name'], rating=problem['rating'], index=problem['index'])
        p.save()

def get_latest_submissions(handle, cnt=500):
    cnt = min(cnt, 2000)
    URL = 'https://codeforces.com/api/user.status?handle={}&from=1&cnt={}'.format(handle, cnt)
    return read_data(URL)

def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def validate_handle(handle):
    URL = 'https://codeforces.com/api/user.info?handles=' + handle

    response = urlopen(URL)
    response_data = json.loads(response.read())

    return response_data['status'] == 'OK'

def submission_to_problem(submission):
    return {
        'contest_id': submission['contestId'],
        'index': submission['problem']['index']
    }

def get_challenge(handle, rating):
    latest_data = get_latest_submissions(handle, 1000)
    latest_data = filter(lambda submission: submission['verdict'] == 'OK', latest_data)
    problem_id_only = map(submission_to_problem, latest_data)
    res = []

    for rt in rating:
        problemset = Problem.objects.filter(rating=rt)
        rproblem = None

        for iteration in range(20):
            problem = problemset[randint(0, len(problemset) - 1)]

            if any(pid['contest_id'] == problem.contest_id and pid['index'] == problem.index for pid in problem_id_only):
                continue

            else:
                rproblem = problem
                break
        
        res.append(rproblem)
        
    return res


