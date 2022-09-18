from django.db import models
from django.utils.translation import gettext_lazy as _
from members.models import Member
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import datetime

first_due_date = datetime.datetime.today() + datetime.timedelta(days=45)
# first_due_default = curr_date.replace(day=1)  # set date to 1st of the month when interest is calculated


class Loan(models.Model):
    name = models.CharField(max_length=150, blank=False, unique=True)
    min_amount = models.FloatField(verbose_name=_('Minimum amount'), blank=False)
    max_amount = models.FloatField(verbose_name=_('Maximum amount'), blank=False)
    repayment_period = models.IntegerField(
        verbose_name=_('Repayment period'),
        blank=True,
        help_text=_('Enter repayment period for this type of loan')
    )
    repayment_period_unit = models.CharField(
        verbose_name=_('Repayment period unit'),
        choices=(('WEEKS', 'Weeks'), ('MONTHS', 'Months')),
        default='MONTHS',
        max_length=50
    )
    interest_rate = models.FloatField(
        verbose_name='Interest rate (p.a.)',
        blank=False,
        max_length=50,
        default=12.0,
    )

    description = models.TextField(verbose_name=_('Description'), blank=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ("view_loans", "Can see loans"),
            ("request_loan", "Can request loan"),
        )


class LoanRequest(models.Model):
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Requesting member'),
        on_delete=models.DO_NOTHING
    )
    loan = models.ForeignKey(Loan, verbose_name=_('Loan type'), on_delete=models.DO_NOTHING,)
    amount_requested = models.FloatField(verbose_name=_('Amount requested'), blank=False)
    date_requested = models.DateTimeField(auto_now_add=True, verbose_name=_('Date requested'), blank=False,)
    details = models.TextField(
        verbose_name=_('More details'),
        blank=True,
        help_text=_('Provide any additional information here'),
    )
    status = models.CharField(
        max_length=100,
        choices=(('pending', _('Pending')), ('approved', _('Approve')), ('rejected', _('Reject')),),
        default='pending'
    )

    def disbursement(self):

        if self.is_disbursed():
            disbursement = Disbursement.objects.get(loan_request_id=self.pk)
        else:
            disbursement = None

        return disbursement

    def guarantors(self):

        """List of members who have been requested to guarantee loan request"""

        return Guarantor.objects.filter(
            loan_request=self.pk
        )

    def is_disbursed(self,):

        try:
            loan_request = Disbursement.objects.filter(loan_request_id=self.pk)
        except ObjectDoesNotExist:
            loan_request = None

        if loan_request.count() > 0:

            return True
        else:
            return False

    def first_due(self,):
        """Returns first_due date for repayment and calculating interests or
        'not disbursed' for pending and rejected loans"""
        try:
            disbursement = Disbursement.objects.get(
                loan_request_id=self.id
            )
            first_due = str(disbursement.first_due.strftime('%Y-%m-%d'))

        except ObjectDoesNotExist:
            first_due = 'not disbursed'

        return first_due

    def next_due(self,):
        """Returns next_due date for repayment and calculating interests or
        the value of first_due() if is not being repaid"""

        repayment = LoanRepayment.objects.filter(
            loan_request_id=self.id
        ).last()

        if repayment is not None:
            next_due = str(repayment.next_due.strftime('%Y-%m-%d'))
        else:
            next_due = self.first_due()

        return next_due

    def is_being_repaid(self,):
        """Returns true or false depending on whether the loan request is being repaid or not"""

        try:
            repayments = LoanRepayment.objects.filter(
                loan_request_id=self.id
            ).count()
        except ObjectDoesNotExist:
            repayments = 0

        if repayments > 0:
            return True
        else:
            return False

    def get_amount_outstanding(self,):
        """Returns the amount outstanding for the particular loan request"""

        if self.is_being_repaid():

            # get amount outstanding
            repayments = LoanRepayment.objects.filter(
                loan_request_id=self.id
            ).last()

            return repayments.outstanding

        else:  # loan is not being repaid, return amount disbursed

            try:
                disbursement = Disbursement.objects.get(
                    amount_disbursed__gt=0,
                    loan_request_id=self.id
                )
                amount_disbursed = disbursement.amount_disbursed

            except ObjectDoesNotExist:  # loan_request_id is not disbursed

                amount_disbursed = 0

            return amount_disbursed

    def get_total_repaid(self):
        """Returns the total amount repaid for the particular loan request."""

        try:
            repayments = LoanRepayment.objects.filter(
                loan_request_id=self.pk
            ).last()

            if repayments is None:  # No repayments yet

                total_repaid = 0

            else:
                total_repaid = repayments.total_paid

        except ObjectDoesNotExist:

            total_repaid = 0

        return total_repaid

    def __str__(self):
        return str(self.loan.name) + ' : ' + str(self.amount_requested)

    class Meta:
        permissions = (
            ("can_manage_loans", "Can manage loans"),
            ("view_requests", "Can see requests"),
        )


class Guarantor(models.Model):
    guarantor = models.ForeignKey(Member, on_delete=models.CASCADE,)
    amount = models.FloatField(max_length=20,)
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.CASCADE)
    status = models.CharField(
        verbose_name=_('Status'),
        choices=(('Pending', 'pending'), ('Approved', 'approved'), ('Rejected', 'rejected')),
        default='pending',
        max_length=50
    )
    response_message = models.TextField(max_length=5000, blank=True)

    def __str__(self):

        return self.guarantor.get_full_name()


class Disbursement(models.Model):
    loan_request = models.OneToOneField(
        LoanRequest,
        unique=True,
        on_delete=models.CASCADE,
        verbose_name=_('Loan request'),
    )
    amount_disbursed = models.FloatField(
        verbose_name=_('Amount disbursed')
    )
    repayment_period_unit = models.CharField(
        verbose_name=_('Repayment period unit'),
        choices=(('months', 'Months'), ('years', 'Years'), ('weeks', 'Weeks'), ('days', 'Days')),
        default='months',
        max_length=50
    )
    interest_rate = models.FloatField(
        verbose_name='Interest rate (p.a.)',
        blank=False,
        max_length=50,
        default=12.0,
    )
    interest_on = models.CharField(
        choices=(
            ('reducing_balance', _('Reducing balance')),
            ('flat_rate', _('Flat rate')),
        ),
        default='reducing_balance',
        max_length=50,
        verbose_name=_('Calculate interest on'),
    )
    repayment_period = models.IntegerField(
        verbose_name=_('Repayment period'),
        blank=True,
        help_text=_('Enter repayment period for this type of loan'),
        default=24
    )
    processing_fee = models.FloatField(
        verbose_name=_('Processing fee'),
        null=True
    )
    date_disbursed = models.DateTimeField(verbose_name=_('Date disbursed'), blank=False, auto_now_add=True)
    first_due = models.DateField(verbose_name=_('Date due'), blank=False, default=first_due_date)
    next_due = models.DateField(verbose_name=_('Next due'), blank=True, )

    def __str__(self):
        return str(self.amount_disbursed)

    class Meta:

        permissions = (
            ("disburse_loan", _("Can make loan disbursements")),
            ("view_loan_disbursements", _("Can see loan disbursements")),
        )

    def get_emi(self):

        disbursement = self

        # Skip fully repaid loans
        amount_outstanding = abs(disbursement.loan_request.get_amount_outstanding())

        if disbursement.repayment_period_unit == 'days':
            epochs = 365
        elif disbursement.repayment_period_unit == 'years':
            epochs = 1
        elif disbursement.repayment_period_unit == 'weeks':
            epochs = 52
        else:
            epochs = 12

        """calculate emi"""

        interest = (disbursement.interest_rate / epochs) / 100

        n = disbursement.repayment_period
        amount = disbursement.amount_disbursed

        if disbursement.interest_on == 'reducing_balance':
            num = ((1 + interest) ** n) - 1
            denm = interest * (1 + interest) ** n
            d = num / denm
            emi = amount / d
        else:  # use flat rate
            total = ((100 + (disbursement.interest_rate * disbursement.repayment_period / epochs)) / 100) * disbursement.amount_disbursed

            emi = total / disbursement.repayment_period

        return emi


class LoanRepayment(models.Model):
    """In future, rename to loan statement"""
    loan_request = models.ForeignKey(
        LoanRequest,
        verbose_name=_('Loan request'),
        on_delete=models.DO_NOTHING,
    )
    payment_date = models.DateTimeField(
        verbose_name=_('Payment date'),
        max_length=100,
        auto_now_add=True
    )
    next_due = models.DateTimeField(
        verbose_name=_('Next due'),
        max_length=100,
        null=True
    )

    credit = models.FloatField(verbose_name=_('Credit'), default=0.0)
    debit = models.FloatField(verbose_name=_('Debit'), default=0.0)
    total_paid = models.FloatField(verbose_name=_('Total paid'), blank=False)
    outstanding = models.FloatField(
        verbose_name=_('Outstanding'),
        blank=False,
        max_length=50,
    )
    interest_epoch = models.CharField(max_length=250, blank=True)
    description = models.CharField(max_length=150, blank=True, default='')
    principal = models.FloatField(blank=True, default=0.0)

    def __str__(self):
        return str(self.payment_date) + " : " + str(self.loan_request)

    class Meta:
        permissions = (
            ("can_repay_loans", _("Can make loan repayment")),
            ("can_disburse_loans", _("Can disburse loans")),
            ("view_loan_repayments", _("Can see loan repayments")),
        )
