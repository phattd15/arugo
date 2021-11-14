[![Twitter](https://img.shields.io/twitter/url?label=%40polarity_iniad&style=social&url=https%3A%2F%2Ftwitter.com%2Fpolarity_iniad)](https://twitter.com/polarity_iniad)
[![Website](https://img.shields.io/website?up_message=arugo&url=https%3A%2F%2Farugo.herokuapp.com%2F)](https://arugo.herokuapp.com/)
[![Blog](https://img.shields.io/website?up_message=codeforces%20blog&url=https%3A%2F%2Fcodeforces.com%2Fblog%2Fentry%2F96830)](https://codeforces.com/blog/entry/96830)


## [Arugo](https://arugo.herokuapp.com/)
Virtual rating system for codeforces using codeforces API.

## Features:
- Problems suggestion.
- Virtual rating for solving problem out-of-contest.
- Make rating graph like in Codeforces
- Challenge timewatch (similar to TLE bot gitgud).

## Built with:
- [Django framework](https://www.djangoproject.com/)
- [Codeforces API](https://codeforces.com/apiHelp)
- [Matplotlib](https://matplotlib.org/)
- [Bootstrap 5](https://getbootstrap.com/)

## Setup:
It is ideal to use virtualenv.

### 1. Fork and clone this project
```
$ git clone https://github.com/polarity-cf/arugo.git
```
### 2. Install dependencies
```
$ pip install -r requirements.txt
```
### 3. Set environment variables
Create ```.env``` file in the ```arugo``` folder.
Change the settings as follow:
```
SECRET_KEY = '<Generate your key @ https://djecrety.ir/>'
DEBUG = True
```
### 4. Migrate
```
$ python manage.py migrate
```
### 5. Fetch the problemset
Run the shell
```
$ python manage.py shell
```
Run the script
```
$ from base.util import fetch_problemset
$ fetch_problemset()
```
