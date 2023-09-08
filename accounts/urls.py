from django.urls import path
from . import views

urlpatterns = [
    path(route="welcome/", view=views.welcome),
]
