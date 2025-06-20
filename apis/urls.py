from django.urls import path
from .api_views import account_views, ai_views, chat_views, mission_views, social_views, love_note_views
from .views import register_device, unregister_device, send_notification, subscribe_device_to_topic, unsubscribe_device_from_topic, send_topic_message

urlpatterns = [
    path('chat-history/', chat_views.HistoryChat.as_view(), name='chat-history'),
    
    # Parent Account APIs
    path('account/init/', account_views.Account_Init, name='account-init'),
    path('account/info/', account_views.Account_Get_Info, name='account-info'),
    path('account/update/', account_views.Account_Update, name='account-update'),
    path('account/delete/', account_views.Account_Delete, name='account-delete'),
    path('account/children/', account_views.Account_Get_Children, name='account-children'),
    
    # Child Account APIs
    path('child/init/', account_views.Child_Init, name='child-init'),
    path('child/info/', account_views.Child_Get_Info, name='child-info'),
    path('child/update/', account_views.Child_Update, name='child-update'),
    path('child/delete/', account_views.Child_Delete, name='child-delete'),
    path('child/bind-status/', account_views.Child_Bind_Status, name='child-bind-status'),
    
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
    path('mission/add/', mission_views.Mission_Add, name='mission-add'),
    path('mission/get/', mission_views.Mission_Get, name='mission-get'),
    path('mission/update/', mission_views.Mission_Update, name='mission-update'),
    path('mission/delete/', mission_views.Mission_Delete, name='mission-delete'),
    path('mission/complete/', mission_views.Mission_Complete, name='mission-complete'),
    path('mission/check-complete/', mission_views.Mission_Check_Completion, name='mission-check-completion'),
    path('mission/add-result/', mission_views.Mission_Add_Result, name='mission-add-result'),
    path('mission/claim/', mission_views.Mission_Claim, name='mission-claim'),
    
    # Love Note APIs
    path('love-note/add/', love_note_views.Love_Note_Add, name='love-note-add'),
    path('love-note/get/', love_note_views.Love_Note_Get, name='love-note-get'),
    path('love-note/update/', love_note_views.Love_Note_Update, name='love-note-update'),
    path('love-note/delete/', love_note_views.Love_Note_Delete, name='love-note-delete'),
    path('love-note/count/', love_note_views.Love_Note_Count, name='love-note-count'),
    
    # Friend APIs
    path('friend/list/', social_views.Get_Friend_List, name='get-friend-list'),
    path('friend/accept/', social_views.Accept_Friend, name='accept-friend'),
    path('friend/reject/', social_views.Reject_Friend, name='reject-friend'),
    path('friend/request/', social_views.Send_Friend_Request, name='send-friend-request'),
    path('friend/remove/', social_views.Remove_Friend, name='remove-friend'),
    path('friend/cancel-request/', social_views.Cancel_Friend_Request, name='cancel-friend-request'),
    path('friend/search/', social_views.Search_User, name='search-user'),
    
    # AI APIs
    path('ai/search/', ai_views.GoogleSearchApi, name='google-search'),
    path('ai/generate-image/', ai_views.GenerateImage, name='generate-image'),
    path('ai/assistant-id/', ai_views.Get_Assistant_ID, name='get-assistant-id'),
    path('ai/camera-input/', ai_views.Camera_Input, name='camera-input'),
    path('ai/homework-input/', ai_views.Homework_Input, name='homework-input'),
    
    # FCM Notification APIs
    path('notification/register-device/', register_device, name='register-device'),
    path('notification/unregister-device/', unregister_device, name='unregister-device'),
    path('notification/send/', send_notification, name='send-notification'),
    
    # Topic-based Notification APIs
    path('notification/topic/subscribe/', subscribe_device_to_topic, name='subscribe-to-topic'),
    path('notification/topic/unsubscribe/', unsubscribe_device_from_topic, name='unsubscribe-from-topic'),
    path('notification/topic/send/', send_topic_message, name='send-topic-notification'),
]
