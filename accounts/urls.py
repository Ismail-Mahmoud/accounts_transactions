from django.urls import path
from . import views

urlpatterns = [
    path(route="", view=views.AccountList.as_view()),
    path(route="<uuid:pk>/", view=views.AccountDetail.as_view()),
    path(route="import/", view=views.UploadViewSet.as_view()),
    path(route="transfer/", view=views.TransferList.as_view()),
]
