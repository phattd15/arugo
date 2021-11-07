from models import Problem
import json
from urllib.request import urlopen

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


