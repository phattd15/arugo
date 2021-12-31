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
- [MongoDB & djongo](https://www.mongodb.com/compatibility/mongodb-and-django)
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
Change the settings as follow, with your mongodb link:
```
SECRET_KEY = '<Generate your key @ https://djecrety.ir/>'
DEBUG = True
DB_URL = 'mongodb+srv://<username>:<password>@<atlas cluster>/<myFirstDatabase>?retryWrites=true&w=majority'
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
