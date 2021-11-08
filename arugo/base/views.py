from django.shortcuts import redirect, render
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

from .util import *

from django.http import HttpResponse

def index(request):
    context = {}
    context['user'] = 'Arugo'

    if request.user.is_authenticated:
        context['user'] = request.user.username
    
    return render(request, 'base/home.html', context)

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
    if request.user.is_authenticated:
        return redirect('home-page')

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
    if request.user.is_authenticated:
        return redirect('home-page')

    context = {}
    context['error'] = []

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        rating = request.POST.get('rating')
        handle = username

        if not represents_int(rating):
            context['error'].append('Rating is not an integer.')

        elif handle.count(' ') > 0 or not validate_handle(handle):
            context['error'].append('This handle does not exists.')

        elif not validate_registration(handle):
            context['error'].append('This handle has not submitted a compile error to 1302I recently.')

        else:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()

                profile = Profile(user=user, handle=handle, virtual_rating=rating, rating_progress=str(rating))
                profile.save()

            return redirect('login')
    
    return render(request, 'base/register.html', context)