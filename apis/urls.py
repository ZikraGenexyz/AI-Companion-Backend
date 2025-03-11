from django.urls import path
from .views import HistoryChat, Login, CreateAccount, AddChat, GetChat

urlpatterns = [
    path('/chats', HistoryChat.as_view()),
    path('/login', Login, name='login'),
    path('/create-account', CreateAccount, name='create-account'),
    path('/add-chat', AddChat, name='add-chat'),
    path('/get-chat', GetChat, name='get-chat'),
]