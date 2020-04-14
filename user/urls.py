from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

URL_PATTERNS = [
    path(
        '',
        views.index,
        name='index'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='user/login.html'),
        name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='/'),
        name='logout'),
    path(
        'signup/',
        views.sign_up,
        name='signup'),
    path(
        'profile/',
        views.profile,
        name='profile'),
]
