from django.db import models

# Create your models here.
class Parents_Accounts(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    date_of_birth = models.DateField(null=True)
    phone_number = models.CharField(max_length=100, null=True)
    relation = models.CharField(max_length=100, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

class Children_Accounts(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Parents_Accounts, on_delete=models.CASCADE, null=True)
    user_id = models.CharField(max_length=100)
    user_info = models.JSONField("User Information", default={
        "name": "",
        "gender": "",
        "birth_date": "",
        "school": "",
        "energy_level": 0,
        "robot_type": 0,
        "robot_color": 0,
    })
    isActive = models.BooleanField(default=True)
    friend_list = models.JSONField("Friends", default={
        "friends": [],
        "pending": [],
        "requests": []
    })
    notification = models.JSONField("Notification", default={
        "missions": [],
        "love_notes": []
    })

class Chat_History(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    isUser = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)