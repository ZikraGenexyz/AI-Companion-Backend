from django.db import models

# Create your models here.
class Chat_History(models.Model):
    id = models.AutoField(primary_key=True)
    user_uid = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    isUser = models.BooleanField(default=False)