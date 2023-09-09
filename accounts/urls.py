from django.urls import path
from . import views

urlpatterns = [
    path(route="welcome/", view=views.welcome),
    path(route="", view=views.AccountsList.as_view()),
    path(route="<uuid:id>/", view=views.AccountInfo.as_view()),
]
