from django.contrib import admin

# Register your models here.

from .models import Problem, Profile

admin.site.register(Problem)
admin.site.register(Profile)
