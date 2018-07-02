from django.db import models
from members.models import Member


class Fine(models.Model):
    credit = models.FloatField(verbose_name='credit', default=0.0)
    debit = models.FloatField(verbose_name='debit', default=0.0)
    amount_outstanding = models.FloatField(verbose_name='Amount outstanding', default=0.0)
    description = models.CharField(verbose_name='Description', max_length=500, blank=False)
    member_account = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='member_account')
    created_by = models.ForeignKey(Member, on_delete=models.DO_NOTHING, related_name='created_by', blank=True,)
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)

    def __str__(self):

        return "%s : %s" % (self.member_account, self.amount_outstanding)







