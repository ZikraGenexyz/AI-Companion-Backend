from django.urls import path
from .views import HistoryChat, AddChat, GetChat, ResetChat, GoogleSearchApi, GenerateImage, Accept_Friend, Reject_Friend, Send_Friend_Request, Remove_Friend, Get_Friend_List, User_Init, Search_User

urlpatterns = [
    path('/chats', HistoryChat.as_view()),
    path('/add-chat', AddChat, name='add-chat'),
    path('/get-chat', GetChat, name='get-chat'),
    path('/reset-chat', ResetChat, name='reset-chat'),
    path('/google-search', GoogleSearchApi, name='google-search-api'),
    path('/generate-image', GenerateImage, name='generate-image'),
    path('/accept-friend', Accept_Friend, name='accept-friend'),
    path('/reject-friend', Reject_Friend, name='reject-friend'),
    path('/send-friend-request', Send_Friend_Request, name='send-friend-request'),
    path('/remove-friend', Remove_Friend, name='remove-friend'),
    path('/get-friend-list', Get_Friend_List, name='get-friend-list'),
    path('/user-init', User_Init, name='user-init'),
    path('/search-user', Search_User, name='search-user'),
]