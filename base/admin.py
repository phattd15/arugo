from django.contrib import admin

from .models import AuthQuery, FetchData, Problem, Profile

# Register your models here.

admin.site.register(Problem)
admin.site.register(Profile)
admin.site.register(AuthQuery)
admin.site.register(FetchData)
