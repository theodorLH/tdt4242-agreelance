from django.urls import path
from . import views

URL_PATTERNS = [
    path('', views.home, name='home'),
]
