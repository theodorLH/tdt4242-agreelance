from django.urls import path
from . import views

URL_PATTERNS = [
    path('<project_id>/<task_id>', views.payment, name='payment'),
    path('<project_id>/<task_id>/receipt/', views.receipt, name='receipt'),
]
