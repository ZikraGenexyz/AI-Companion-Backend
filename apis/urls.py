from django.urls import path
from .views import HistoryChat, AddChat, GetChat, ResetChat, GoogleSearchApi

urlpatterns = [
    path('/chats', HistoryChat.as_view()),
    path('/create-account', CreateAccount, name='create-account'),
    path('/check-user', CheckUser, name='check-user-availability'),
    path('/add-chat', AddChat, name='add-chat'),
    path('/get-chat', GetChat, name='get-chat'),
    path('/reset-chat', ResetChat, name='reset-chat'),
    path('/get-deepgram-api', GetDeepgramAPI, name='get-deepgram-api'),
    path('/google-search', GoogleSearchApi, name='google-search-api'),
]