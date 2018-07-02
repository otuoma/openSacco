from shares.models import Share, MemberShare
from dividends.models import DividendDisbursement
from fines.models import Fine
from loans.models import LoanRepayment, Disbursement
from payments.models import Payment, PaymentType
from pettycash.models import Expenditure
from django.db.models import Sum
from django.utils import timezone
from accounting.models import BuiltInAccount, AccountTransaction
from django.core.exceptions import ObjectDoesNotExist


try:
    builtin_accounts = [('none', '--')] + [(account.slug, account.account_name) for account in BuiltInAccount.objects.all()]
except:
    builtin_accounts = [('none', '--')]


def get_account_balance(account, request):

    if request.GET.get('date_from'):
        date_from = request.GET.get('date_from') + ' 00:00:00'
    else:
        date_from = '2000-01-01 00:00:00'

    if request.GET.get('date_to'):
        date_to = request.GET.get('date_to') + ' 23:59:59'
    else:
        date_to = timezone.datetime.today() + timezone.timedelta(hours=23, minutes=59, seconds=59)

    # Query active accounts only or get supplied val

    status = request.GET.get('status', 'all')

    opening_balance = account.opening_balance

    account_transactions = 0.0

    if not account.inherits == 'none':  # is a builtin account

        try:
            payment_type = PaymentType.objects.get(slug=account.inherits)

            account_transactions = Payment.objects.filter(
                payment_type_id=payment_type.pk,
                payment_type__slug=account.inherits,
                date__gte=date_from,
                date__lte=date_to
            )

            account_transactions = account_transactions.aggregate(Sum('amount'))['amount__sum']

        except ObjectDoesNotExist:  # is builtin account BUT is neither savings nor reg fees

            if account.inherits == 'fines_paid':
                fines = Fine.objects.filter(
                    date__gte=date_from,
                    date__lte=date_to
                )
                total_credit = fines.aggregate(Sum('credit'))

                if total_credit['credit__sum'] is None:
                    total_credit['credit__sum'] = 0.0

                account_transactions = total_credit['credit__sum']

            elif account.inherits == 'fines_unpaid':
                fines = Fine.objects.filter(
                    date__gte=date_from,
                    date__lte=date_to
                )
                total_credit = fines.aggregate(Sum('debit'))

                if total_credit['debit__sum'] is None:
                    total_credit['debit__sum'] = 0.0

                account_transactions = total_credit['debit__sum']

            elif account.inherits == 'loan_processing_fees':

                disbursed_loans = Disbursement.objects.filter(
                    date_disbursed__gte=date_from,
                    date_disbursed__lte=date_to
                )

                account_transactions = disbursed_loans.aggregate(Sum('processing_fee'))['processing_fee__sum']

            elif account.inherits == 'loan_disbursements':

                disbursed_loans = Disbursement.objects.filter(
                    date_disbursed__gte=date_from,
                    date_disbursed__lte=date_to
                )

                account_transactions = disbursed_loans.aggregate(Sum('amount_disbursed'))['amount_disbursed__sum']

            elif account.inherits == 'loan_repayments':

                loan_repayments = LoanRepayment.objects.filter(
                    payment_date__gte=date_from,
                    payment_date__lte=date_to
                )
                account_transactions = loan_repayments.aggregate(Sum('credit'))['credit__sum']

            elif account.inherits == 'petty_cash':

                expenditure_list = Expenditure.objects.filter(
                    date__gte=date_from,
                    date__lte=date_to
                ).order_by('-date')

                total = expenditure_list.aggregate(Sum('amount'))

                account_transactions = total['amount__sum']

            elif account.inherits == 'dividend_disbursements':

                disbursements = DividendDisbursement.objects.filter(
                    date__gte=date_from,
                    date__lte=date_to
                )

                account_transactions = disbursements.aggregate(Sum('amount'))['amount__sum']

            elif account.inherits == 'shares':
                share = Share.objects.first()
                shares = MemberShare.objects.all().order_by('-pk')

                if share is None:
                    share_value = 0
                    aggregate = None
                else:
                    share_value = share.share_value
                    aggregate = shares.aggregate(Sum('quantity'))

                account_transactions = share_value * aggregate['quantity__sum']

    else:  # is not a builtin account
        account_transactions = AccountTransaction.objects.filter(
            account_id=account.pk,
            date__gte=date_from,
            date__lte=date_to
        )

        account_transactions = account_transactions.aggregate(Sum('amount'))['amount__sum']

    if account_transactions is None:
        account_transactions = 0.0

    balance = opening_balance + account_transactions

    return balance




