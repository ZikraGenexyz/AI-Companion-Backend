from django.urls import path
from .views import HistoryChat, AddChat, GetChat, ResetChat, GoogleSearchApi, GenerateImage

urlpatterns = [
    path('/chats', HistoryChat.as_view()),
    path('/add-chat', AddChat, name='add-chat'),
    path('/get-chat', GetChat, name='get-chat'),
    path('/reset-chat', ResetChat, name='reset-chat'),
    path('/google-search', GoogleSearchApi, name='google-search-api'),
    path('/generate-image', GenerateImage, name='generate-image'),
]