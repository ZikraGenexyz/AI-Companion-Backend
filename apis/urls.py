from django.urls import path
from .views import ListUser, HistoryChat

urlpatterns = [
    path('', ListUser.as_view()),
    path('/chats', HistoryChat.as_view()),
]