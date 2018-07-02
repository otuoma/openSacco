from django.db import models
from members.models import Member


class Share(models.Model):
    share_value = models.FloatField(max_length=50)


class MemberShare(models.Model):

    member = models.OneToOneField(Member, on_delete=models.DO_NOTHING, unique=True)
    quantity = models.IntegerField(default=0)


