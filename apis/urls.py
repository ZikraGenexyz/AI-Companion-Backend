from django.urls import path
from .views import ListUser, HistoryChat
from .views import Login

urlpatterns = [
    path('', ListUser.as_view()),
    path('chats', HistoryChat.as_view()),
    path('login', Login(), name='login'),
]