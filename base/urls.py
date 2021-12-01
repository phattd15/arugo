from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("list/", views.challenge_list, name="list"),
    path("solving/<int:contest_id>/<str:index>/", views.solving, name="solve"),
    path("challenge/", views.challenge_site, name="challenge"),
    path("giveup/", views.giveup, name="giveup"),
    path("reset_progress/", views.reset_progress, name="reset-progress"),
    path("help/", views.help, name="help"),
    path("validate/", views.validate, name="validate"),
    path("discard/", views.discard, name="discard"),
    path("", views.index, name="home-page"),
    path("test/", views.testing, name="test"),
]
