from django.urls import path
from .views import account_views, ai_views, chat_views, mission_views, social_views
from .views import HistoryChat

urlpatterns = [
    path('chat-history/', HistoryChat.as_view(), name='chat-history'),
    
    # Account APIs
    path('account/init/', account_views.Account_Init, name='account-init'),
    path('account/update/', account_views.Account_Update, name='account-update'),
    path('account/info/', account_views.Account_Get_Info, name='account-info'),
    path('account/delete/', account_views.Account_Delete, name='account-delete'),
    
    # Child Account APIs
    path('child/init/', account_views.Child_Init, name='child-init'),
    path('child/bind-status/', account_views.Child_Bind_Status, name='child-bind-status'),
    path('child/edit/', account_views.Edit_Child, name='child-edit'),
    path('child/info/', account_views.Get_Child_Info, name='child-info'),
    path('children/', account_views.Get_Children, name='children'),
    
    # User Management APIs
    path('user/add/', account_views.Add_User, name='add-user'),
    path('user/remove/', account_views.Remove_User, name='remove-user'),
    path('user/update/', account_views.Update_User, name='update-user'),
    path('account/users/', account_views.Get_Account_Users, name='account-users'),
    
    # Binding APIs
    path('binding/create-otp/', account_views.Create_Bind_OTP, name='create-bind-otp'),
    path('binding/verify-otp/', account_views.Verify_Bind_OTP, name='verify-bind-otp'),
    path('binding/unbind/', account_views.Unbind_Children_Account, name='unbind'),
    path('binding/bind/', account_views.Bind_Children_Account, name='bind'),
    
    # Chat APIs
    path('chat/reset/', chat_views.ResetChat, name='reset-chat'),
    path('chat/get/', chat_views.GetChat, name='get-chat'),
    path('chat/add/', chat_views.AddChat, name='add-chat'),
    
    # Mission APIs
    path('mission/get/', mission_views.Get_Missions, name='get-missions'),
    path('mission/add/', mission_views.Add_Mission, name='add-mission'),
    path('mission/complete/', mission_views.Complete_Mission, name='complete-mission'),
    path('mission/edit/', mission_views.Edit_Mission, name='edit-mission'),
    path('mission/delete/', mission_views.Delete_Mission, name='delete-mission'),
    path('mission/check-completion/', mission_views.Check_Homework_Completion, name='check-homework-completion'),
    
    # Love Note APIs
    path('love-note/get/', mission_views.Get_Love_Notes, name='get-love-notes'),
    path('love-note/add/', mission_views.Add_Love_Note, name='add-love-note'),
    path('love-note/remove/', mission_views.Remove_Love_Note, name='remove-love-note'),
    path('love-note/edit/', mission_views.Edit_Love_Note, name='edit-love-note'),
    
    # Friend APIs
    path('friend/list/', social_views.Get_Friend_List, name='get-friend-list'),
    path('friend/accept/', social_views.Accept_Friend, name='accept-friend'),
    path('friend/reject/', social_views.Reject_Friend, name='reject-friend'),
    path('friend/remove/', social_views.Remove_Friend, name='remove-friend'),
    path('friend/request/', social_views.Send_Friend_Request, name='send-friend-request'),
    path('friend/cancel-request/', social_views.Cancel_Friend_Request, name='cancel-friend-request'),
    path('friend/search/', social_views.Search_User, name='search-user'),
    
    # AI APIs
    path('ai/search/', ai_views.GoogleSearchApi, name='google-search'),
    path('ai/generate-image/', ai_views.GenerateImage, name='generate-image'),
    path('ai/assistant-id/', ai_views.Get_Assistant_ID, name='get-assistant-id'),
    path('ai/camera-input/', ai_views.Camera_Input, name='camera-input'),
    path('ai/homework-input/', ai_views.Homework_Input, name='homework-input'),
]
