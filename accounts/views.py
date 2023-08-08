from django.contrib.auth import authenticate, get_user_model, login
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import *


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                login(request, user)
                return redirect('/profile')
        return render(request, 'registration/login.html', {'error': True})