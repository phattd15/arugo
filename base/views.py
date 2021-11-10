from django.shortcuts import redirect, render
from .models import Profile, Problem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

from .util import *


def index(request):
    context = {}
    context["user"] = None
    context["graph"] = None

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        context["user"] = profile
        context["graph"] = make_graph(eval(profile.rating_progress))

    return render(request, "home.html", context)


def challenge_list(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    profile = Profile.objects.get(user=user)

    print(user, profile.in_progress, profile.current_problem)

    if profile.in_progress:
        return redirect("challenge")

    handle = profile.handle
    rating = profile.virtual_rating

    normalized_rating = rating - rating % 100
    context = {}

    context["challenges"] = get_challenge(
        handle, [normalized_rating + delta for delta in range(-200, 500, 100)]
    )

    return render(request, "list.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home-page")

    context = {}
    context["error"] = []

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            response = redirect("home-page")
            return response

        else:
            context["error"].append("Failed to login.")

    return render(request, "login.html", context)


def logout_view(request):
    logout(request)

    return redirect("/login/")


def register(request):
    if request.user.is_authenticated:
        return redirect("home-page")

    context = {}
    context["error"] = []

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        rating = request.POST.get("rating")
        handle = username

        if not represents_int(rating):
            context["error"].append("Rating is not an integer.")

        elif handle.count(" ") > 0 or not validate_handle(handle):
            context["error"].append("This handle does not exists.")

        elif not validate_registration(handle):
            context["error"].append(
                "This handle has not submitted a compile error to 1302I recently."
            )

        else:
            rating = int(rating)

            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()

                profile = Profile.objects.get(handle=handle)
                apply_rating_change(profile, rating, True)

            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()

                profile = Profile(
                    user=user,
                    handle=handle,
                    virtual_rating=rating,
                    rating_progress="[" + str(rating) + "]",
                )
                profile.save()

            return redirect("login")

    return render(request, "register.html", context)


def challenge_site(request):
    if not request.user.is_authenticated:
        return redirect("home-page")

    user = request.user
    profile = Profile.objects.get(user=user)

    if not profile.in_progress:
        return redirect("list")

    if validate_challenge(profile):
        return redirect("list")

    contest_id, index = parse_problem_id(profile.current_problem)
    problem = Problem.objects.get(contest_id=contest_id, index=index)
    color, bg_color = rating_color(problem.rating)

    context = {}
    context["problem"] = problem
    context["time_remaining"] = (profile.deadline - timezone.now()).total_seconds()
    context["color"] = color
    context["bg_color"] = bg_color

    return render(request, "challenge.html", context)


def solving(request, contest_id, index):
    if not request.user.is_authenticated:
        return redirect("home-page")

    user = request.user
    profile = Profile.objects.get(user=user)

    if profile.in_progress:
        return redirect("challenge")

    accept_challenge(profile, contest_id, index)

    return redirect("challenge")


def giveup(request):
    if not request.user.is_authenticated:
        return redirect("home-page")

    user = request.user
    profile = Profile.objects.get(user=user)

    # TODO: Make a give up function in util
    if profile.in_progress:
        give_up_problem(profile)

    return redirect("list")

def reset_progress(request):
    if not request.user.is_authenticated:
        return redirect("home-page")

    user = request.user
    profile = Profile.objects.get(user=user)

    reset_rating_progress(profile)
    return redirect("home-page")