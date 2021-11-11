from django.db import models
from django.contrib.auth.models import User

# Create your models here.

"""
Codeforces problems. Fetch locally.
Variables are named accordingly to the api.
"""


class Problem(models.Model):
    contest_id = models.IntegerField(default=1)
    name = models.CharField(max_length=200)
    rating = models.IntegerField(default=1500)
    index = models.CharField(max_length=4)

    def __str__(self):
        return (
            str(self.contest_id)
            + self.index
            + ": "
            + self.name
            + ", rating = "
            + str(self.rating)
        )


"""
Profile hereby inherits the django user.
handle = codeforces handle
rating_progress = python list stored in string type through 'repr' method, later parse by eval
"""


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    handle = models.CharField(max_length=40)
    registration_date = models.DateField(auto_now_add=True)
    rating_progress = models.CharField(max_length=1000, default="[]")
    virtual_rating = models.IntegerField(default=1400)
    in_progress = models.BooleanField(default=False)
    current_problem = models.CharField(max_length=20, default="Unselected")
    deadline = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.handle
