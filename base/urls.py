from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("list/", views.challenge_list, name="list"),
    path("solving/<int:contest_id>/<str:index>/", views.solving, name="solve"),
    path("challenge/", views.challenge_site, name="challenge"),
    path("", views.index, name="home-page"),
]
