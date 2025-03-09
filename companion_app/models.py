from django.db import models

# Create your models here.
class User_Data(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    password = models.CharField(max_length=200)
    

class Chat_History(models.Model):
    key = models.ForeignKey(User_Data, related_name='chats', on_delete=models.CASCADE)
    chat = models.TextField()