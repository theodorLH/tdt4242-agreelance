from django.http import HttpResponse
from django.db import models
from django.db.models.signals import post_save
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.dispatch import receiver
from projects.models import ProjectCategory
from .forms import SignUpForm


def index(request):
    return render(request, 'base.html')


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.company = form.cleaned_data.get('company')
            user.is_active = False
            user.profile.categories.add(*form.cleaned_data['categories'])
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            messages.success(
                request,
                'Your account has been created and is awaiting verification.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})


@login_required
def profile(request):
    old_user = request.user
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.company = form.cleaned_data.get('company')
            user.is_active = True
            user.profile.categories.add(*form.cleaned_data['categories'])
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            old_user.delete()
            messages.success(
                request, 'Your account has been reneewed. Sign in to continue')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'user/profile.html', {'form': form})
