from django.db import models

# Create your models here.
class Accounts(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    date_joined = models.DateTimeField(auto_now_add=True)

class Account_Users(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    isParent = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)
    friend_list = models.JSONField("Friends", default={
        "friends": [],
        "pending": [],
        "requests": []
    })
    notification = models.JSONField("Notification", default={})

class Chat_History(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    isUser = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    