from django.db import models
from members.models import Member
from django.utils import timezone
# from datetime import datetime
from django.utils.translation import ugettext_lazy as _

class TrialBalance(models.Model):
    credit = models.FloatField(max_length=50)
    debit = models.FloatField(max_length=50)
    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
        blank=False,
        auto_now_add=True
    )
    module = models.CharField(
        max_length=100,
        choices=(
            ('Shares', 'shares'),
            ('Contributions', 'contributions'),
            ('Loans', 'loans'),
            ('Fines', 'fines'),
        ),
    )
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    staff = models.CharField(max_length=50, blank=False, default='')
    description = models.CharField(max_length=250, default='')

