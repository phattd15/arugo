from django.shortcuts import redirect, render
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

from .util import get_challenge, get_latest_submissions, represents_int, validate_handle

from django.http import HttpResponse

def index(request):
    if request.user.is_authenticated:
        print(request.user)
        return HttpResponse("Hello, " + str(request.user))
    return HttpResponse("Hello, aurgo.")

def challenge_list(request):

    if request.user.is_authenticated:
        
        user = request.user
        profile = Profile.objects.get(user=user)

        handle = profile.handle
        rating = profile.virtual_rating

        normalized_rating = rating - rating % 100
        context = {}

        context['challenges'] = get_challenge(handle, [normalized_rating + delta for delta in range(-100, 400, 100)])

        return render(request, 'base/list.html', context)

    else:
        return redirect('login')

# def in_challenge(request);
#     if request.user.is_authenticated:
#         context = []
#     else:
#         return redirect('login')

def login_view(request):
    context = {}
    context['error'] = 'Please login with registered user and password'

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            response = redirect('home-page')
            return response

        else:
            context['error'] = 'Failed to login.'
        
    return render(request, 'base/login.html', context)

def logout_view(request):
    logout(request)

    return redirect('/login/')

def register(request):
    context = {}
    context['error'] = ""

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        rating = request.POST.get('rating')
        handle = request.POST.get('handle')

        if User.objects.filter(username=username).exists():
            context['error'] += 'This username exists in the database.'

        elif not represents_int(rating):
            context['error'] += 'Rating is not an integer.'

        elif handle.count(' ') > 0 or not validate_handle(handle):
            context['error'] += 'This handle does not exists.'

        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()

            profile = Profile(user=user, handle=handle, virtual_rating=rating, rating_progress="")
            profile.save()

            return redirect('login')
    
    return render(request, 'base/register.html', context)