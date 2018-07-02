from django.db import models
from members.models import Member


class Notification(models.Model):
    title = models.CharField(max_length=150, default='')
    notification = models.TextField(verbose_name='message', max_length=5000)
    to = models.ForeignKey(Member, on_delete=models.CASCADE,)
    sender = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='sender')
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


