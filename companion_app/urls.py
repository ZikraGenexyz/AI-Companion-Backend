from django.urls import path
from . import views

urlpatterns = [
    path('', views.myapp, name='myapp'),
    path('process-audio/', views.process_audio, name='process_audio'),
]