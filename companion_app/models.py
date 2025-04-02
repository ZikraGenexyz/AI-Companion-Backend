from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    username = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

class Chat_History(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    isUser = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

class Friends(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    friend_list = models.JSONField("Friends", default={})
    notification = models.JSONField("Notification", default={})

    