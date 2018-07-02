from django.db import models
from django.utils.translation import ugettext_lazy as _
# from members.models import Member
from django.conf import settings
from django.db.models import Sum


class PaymentType(models.Model):

    payment_type = models.CharField(
        verbose_name=_('Payment type'),
        max_length=150, blank=False,
        unique=True
    )
    frequency = models.CharField(
        verbose_name=_('Frequency'),
        choices=(('UNSET', 'Unset'), ('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')),
        default='UNSET', max_length=100,
    )
    min_amount = models.IntegerField(verbose_name=_('Minimum amount'), blank=False)
    date_created = models.DateTimeField(verbose_name='Date created', auto_now=True)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(default=str(payment_type).replace(' ', '_').lower(), max_length=250)
    flag = models.CharField(
        verbose_name='Flag',
        choices=(
            ('saving_account', 'Saving account'),
            ('registration_fee', 'Registration Fees'),
        ),
        default='saving_account',
        max_length=150,
    )

    def __str__(self):
        return self.payment_type

    class Meta:
        permissions = (
            ('view_payment_type', 'Can view payment types'),
        )


class Payment(models.Model):

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Members name'),
        related_name='member',
        on_delete=models.DO_NOTHING
    )
    payment_type = models.ForeignKey(PaymentType, on_delete=models.DO_NOTHING, verbose_name='Payment category')
    amount = models.FloatField(verbose_name=_('Amount'), blank=False)
    date = models.DateTimeField(verbose_name=_('Date time'),)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Paid by'),
        on_delete=models.DO_NOTHING,
        related_name='staff',
    )
    notes = models.TextField(verbose_name=_('Notes'), max_length=1000, blank=True)
    total = models.FloatField(verbose_name=_('Total'), blank=False, default=0)

    class Meta:
        permissions = (
            ('view_own_payment', 'Can view own payments'),
            ('view_all_payments', 'Can view all payments'),
        )

    def loan_amount_repaid_by_member(self, member_id):
        total_loans_repaid = Payment.objects.filter(
            member_id=member_id,
            payment_type__flag='loan_repayment'
        ).aggregate(Sum('amount'))

        return total_loans_repaid

    def __str__(self):
        return self.member.last_name + ' : ' + str(self.amount)

