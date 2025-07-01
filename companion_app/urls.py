from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.myapp, name='myapp'),
    path('process-audio/', views.process_audio, name='process_audio'),
    path('v1/', include('apis.urls')),
]