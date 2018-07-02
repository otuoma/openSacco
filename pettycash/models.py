from django.db import models
from members.models import Member


class Expenditure(models.Model):
    amount = models.IntegerField(verbose_name='Amount', blank=False, default=0)
    description = models.TextField(max_length=250, verbose_name='Description', blank=False, help_text='')
    date = models.DateTimeField(blank=False, verbose_name='Date')
    edited = models.DateTimeField(blank=False, verbose_name='Edited', auto_now=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)