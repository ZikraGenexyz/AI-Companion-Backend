from django.urls import path
from .views import HistoryChat
from .views import Login, CreateAccount

urlpatterns = [
    path('/chats', HistoryChat.as_view()),
    path('/login', Login, name='login'),
    path('/create-account', CreateAccount, name='create-account'),
]