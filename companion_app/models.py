from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat_History(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    isUser = models.BooleanField(default=False)