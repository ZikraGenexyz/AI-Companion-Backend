from django.urls import path
from .views import *

urlpatterns = [
    # Chats
    path('/chats', HistoryChat.as_view()),
    path('/add-chat', AddChat, name='add-chat'),
    path('/get-chat', GetChat, name='get-chat'),
    path('/reset-chat', ResetChat, name='reset-chat'),

    # Friends
    path('/accept-friend', Accept_Friend, name='accept-friend'),
    path('/reject-friend', Reject_Friend, name='reject-friend'),
    path('/send-friend-request', Send_Friend_Request, name='send-friend-request'),
    path('/remove-friend', Remove_Friend, name='remove-friend'),
    path('/get-friend-list', Get_Friend_List, name='get-friend-list'),
    path('/search-user', Search_User, name='search-user'),
    path('/cancel-friend-request', Cancel_Friend_Request, name='cancel-friend-request'),
    
    # Account
    path('/get-account-users', Get_Account_Users, name='get-account-users'),
    path('/account-init', Account_Init, name='account-init'),
    path('/account-update', Account_Update, name='account-update'),
    
    # User
    path('/add-user', Add_User, name='add-user'),
    path('/remove-user', Remove_User, name='remove-user'),
    path('/update-user', Update_User, name='update-user'),
    
    # Assistant
    path('/get-assistant-id', Get_Assistant_ID, name='get-assistant-id'),
    
    # Bind
    path('/create-bind-otp', Create_Bind_OTP, name='create-bind-otp'),
    path('/verify-bind-otp', Verify_Bind_OTP, name='verify-bind-otp'),

    # Love Note
    path('/get-love-notes', Get_Love_Notes, name='get-love-notes'),
    path('/add-love-note', Add_Love_Note, name='add-love-note'),
    path('/remove-love-note', Remove_Love_Note, name='remove-love-note'),
    path('/edit-love-note', Edit_Love_Note, name='edit-love-note'),
    
    # Child
    path('/child-init', Child_Init, name='child-init'),
    path('/get-children', Get_Children, name='get-children'),
    path('/edit-child', Edit_Child, name='edit-child'),
    path('/get-child-info', Get_Child_Info, name='get-child-info'),
    
    # Child Bind
    path('/child-bind-status', Child_Bind_Status, name='child-bind-status'),
    path('/unbind-children-account', Unbind_Children_Account, name='unbind-children-account'),
    path('/bind-children-account', Bind_Children_Account, name='bind-children-account'),
    
    # Mission
    path('/get-missions', Get_Missions, name='get-missions'),
    path('/add-mission', Add_Mission, name='add-mission'),
    path('/complete-mission', Complete_Mission, name='complete-mission'),
    path('/edit-mission', Edit_Mission, name='edit-mission'),
    path('/delete-mission', Delete_Mission, name='delete-mission'),
    path('/check-homework-completion', Check_Homework_Completion, name='check-homework-completion'),
    
    # AI
    path('/google-search', GoogleSearchApi, name='google-search-api'),
    path('/generate-image', GenerateImage, name='generate-image'),
    path('/openai/camera-input', Camera_Input, name='camera-input'),
    path('/openai/homework-input', Homework_Input, name='homework-input'),
]
