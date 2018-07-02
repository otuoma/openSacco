from django.db import models
import random
from members.models import Member
from django.db.models import Sum, Max
from payments.models import Payment
from shares.models import Share, MemberShare
from loans.models import LoanRepayment, LoanRequest, Disbursement
from fines.models import Fine
from pettycash.models import Expenditure
from dividends.models import DividendDisbursement
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class AccountGroup(models.Model):
    group_number = models.IntegerField(blank=False, unique=True)
    group_name = models.CharField(max_length=150, blank=False)
    description = models.TextField(max_length=250, blank=True)

    def __str__(self):

        return str(self.group_number) + ": " + self.group_name

    def get_children(self):

        return Account.objects.filter(account_group=self.pk).order_by('account_number')


class BuiltInAccount(models.Model):
    account_name = models.CharField(max_length=250)
    slug = models.CharField(
        max_length=250,
        default=str(account_name).replace(' ', '_').lower(),
        unique=True
    )

    def __str__(self):

        return self.account_name


class Account(models.Model):

    account_group = models.ForeignKey(AccountGroup, on_delete=models.DO_NOTHING, null=True)
    account_number = models.IntegerField(default=random.randint(1, 10000), unique=True)
    account_name = models.CharField(max_length=250)
    inherits = models.CharField(max_length=250, default='none')
    account_type = models.CharField(
        max_length=250,
        choices=(
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('expense', 'Expense'),
            ('equity', 'Equity'),
            ('revenue', 'Revenue'),
            ('other_account', 'Other Account'),
        ),
        default='liability'
    )
    increases = models.CharField(
        max_length=250,
        choices=(
            ('credit', 'Credit'),
            ('debit', 'Debit')
        ),
        default='debit'
    )
    status = models.CharField(
        max_length=250,
        choices=(
            ('active', 'Active'),
            ('closed', 'Closed')
        ),
        default='active'
    )
    opening_balance = models.FloatField(default=0.0,)
    opening_date = models.DateField(default=timezone.datetime.now)
    description = models.TextField(max_length=1000, blank=True)

    def get_balance(self):

        opening_balance = self.opening_balance

        account_transactions = 0.0

        if self.inherits == 'saving_accounts':

            contributions_sum = Payment.objects.filter(
                payment_type__flag='saving_account',
                payment_type__is_active=True
            ).aggregate(Sum('amount'))

            contributions = contributions_sum['amount__sum']

            account_transactions = contributions

        elif self.inherits == 'registration_fees':

            contributions_sum = Payment.objects.filter(
                payment_type__flag='registration_fee',
                payment_type__is_active=True
            ).aggregate(Sum('amount'))

            contributions = contributions_sum['amount__sum']

            account_transactions = contributions
        elif self.inherits == 'shares':

            share = Share.objects.first()
            shares = MemberShare.objects.all().order_by('-pk')

            if share is None:
                share_value = 0
                aggregate = None
            else:
                share_value = share.share_value
                aggregate = shares.aggregate(Sum('quantity'))

            account_transactions = share_value * aggregate['quantity__sum']

        elif self.inherits == 'loan_disbursements':

            disbursed_loans = Disbursement.objects.all()

            account_transactions = disbursed_loans.aggregate(Sum('amount_disbursed'))['amount_disbursed__sum']

        elif self.inherits == 'loan_processing_fees':

            disbursed_loans = Disbursement.objects.all()

            account_transactions = disbursed_loans.aggregate(Sum('processing_fee'))['processing_fee__sum']

        elif self.inherits == 'loan_repayments':

            loan_repayments = LoanRepayment.objects.all()

            account_transactions = loan_repayments.aggregate(Sum('credit'))['credit__sum']

        elif self.inherits == 'fines_paid':

            fines = Fine.objects.all()
            total_credit = fines.aggregate(Sum('credit'))

            if total_credit['credit__sum'] is None:
                total_credit['credit__sum'] = 0.0

            account_transactions = total_credit['credit__sum']

        elif self.inherits == 'fines_unpaid':

            fines = Fine.objects.all()
            total_debit = fines.aggregate(Sum('debit'))

            if total_debit['debit__sum'] is None:
                total_debit['debit__sum'] = 0.0

            total_credit = fines.aggregate(Sum('credit'))

            if total_credit['credit__sum'] is None:
                total_credit['credit__sum'] = 0.0

            account_transactions = total_debit['debit__sum'] - total_credit['credit__sum']

        elif self.inherits == 'petty_cash':

            expenditure_list = Expenditure.objects.all().order_by('-date')

            total = expenditure_list.aggregate(Sum('amount'))

            account_transactions = total['amount__sum']

        elif self.inherits == 'dividend_disbursements':

            disbursements = DividendDisbursement.objects.all()

            account_transactions = disbursements.aggregate(Sum('amount'))['amount__sum']

        balance = opening_balance + account_transactions

        return balance

    def __str__(self):

        return str(self.account_number) + ": " + self.account_name


class AccountTransaction(models.Model):
    amount = models.FloatField(default=0.0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    narration = models.TextField(max_length=500)
    date = models.DateTimeField(auto_created=True)
    member = models.CharField(default='none', max_length=250)
    staff = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):

        return '%s for %s : %s' % (self.account, self.member, self.amount)



