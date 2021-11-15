from django.contrib import admin

# Register your models here.

from .models import AuthQuery, FetchData, Problem, Profile

admin.site.register(Problem)
admin.site.register(Profile)
admin.site.register(AuthQuery)
admin.site.register(FetchData)
