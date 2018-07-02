from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from .managers import UserManager
from payments.models import Payment
from django.db.models import Sum
# from notifications.models import Notification
from django.utils.translation import ugettext_lazy as _


class Member(AbstractUser):

    member_number = models.CharField(verbose_name=_('Member number'), blank=True, null=True, max_length=50)
    first_name = models.CharField(verbose_name=_('First Name'), blank=False, max_length=100)
    last_name = models.CharField(verbose_name=_('Last Name'), blank=False, max_length=100)
    national_id = models.IntegerField(verbose_name=_('National ID Number'), null=True)
    phone_number = models.CharField(max_length=50, unique=True, verbose_name=_('Phone Number'))
    email = models.EmailField(verbose_name=_('Email'), unique=True, max_length=100, blank=False)
    username = models.CharField(verbose_name=_('User name'), max_length=50, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    scanned_id = models.FileField(upload_to='scanned_ids/', null=True,)
    dob = models.DateField(verbose_name=_('Date of birth'), max_length=250, blank=True, default='1990-01-01')
    nationality = models.CharField(verbose_name=_('Nationality'), max_length=50, blank=True, null=True, default='Kenyan')
    postal_address = models.CharField(verbose_name=_('Postal address'), max_length=200, blank=True, null=True)
    city = models.CharField(verbose_name=_('City'), max_length=200, blank=True, null=True)
    street = models.CharField(verbose_name=_('Street or road'), max_length=200, blank=True, null=True)
    house = models.CharField(verbose_name=_('House or plot number'), max_length=200, blank=True, null=True)
    occupation = models.CharField(verbose_name=_('Occupation'), max_length=200, blank=True, null=True)
    employer = models.CharField(verbose_name=_('Employer'), max_length=250, blank=True)
    marital_status = models.CharField(
        verbose_name=_('Marital Status'),
        max_length=50,
        choices=(
            ('single', _('Single')),
            ('married', _('Married')),
            ('divorced', _('Divorced')),
            ('other', _('Other')),
        ),
        default='single'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['national_id', 'first_name', 'last_name', 'phone_number']

    class Meta:

        verbose_name = _('member')
        verbose_name_plural = _('members')
        permissions = (
            ('can_view_members', _('Can view members')),
            ('can_change_members', _('Can change members')),
            ('can_delete_members', _('Can delete members')),
        )

    def validate_member_number(self, member_number=''):
        member = Member.objects.get(member_number=member_number)
        if member:
            raise ValidationError(
                _('%(member_number)s already exist'),
                params={'member_number': member_number},
            )

    def get_short_name(self):
        '''
        Returns the last name for the user.
        '''
        return self.last_name

    def member_total_contributions(self,):

        """Returns total contributions of a member"""

        total_contributions = Payment.objects.filter(
            member_id=self.pk,
            payment_type__flag='contribution'
        )

        if len(total_contributions) > 0:

            total = total_contributions.aggregate(Sum('amount'))['amount__sum']

        else:
            total = 0

        return total

    def __str__(self):
        return self.get_full_name()


# class PasswordToken(models.Model):
#     token = models.CharField(max_length=150, blank=False)
#     member = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
#     requested = models.DateTimeField(auto_now_add=True)
#     expired = models.DateTimeField(blank=True)
#     is_active = models.BooleanField(default=True)


class BankAccount(models.Model):
    bank = models.CharField(blank=False, verbose_name='Bank Name', max_length=250)
    account_name = models.CharField(max_length=250)
    account_number = models.CharField(max_length=50, blank=False, unique=True)
    branch = models.CharField(verbose_name='Branch', max_length=150)
    member = models.ForeignKey(Member, blank=False, on_delete=models.DO_NOTHING,)


