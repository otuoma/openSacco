from loans.models import (LoanRepayment, LoanRequest, Disbursement)
import datetime, calendar
from django.utils import timezone


now = datetime.datetime.now()


def run():

    print('===============Starting script========================\n')

    date_today = datetime.datetime.today()

    disbursements = Disbursement.objects.filter(
        next_due=date_today.strftime('%Y-%m-%d')
    )

    if disbursements.count() > 0:

        for disbursement in disbursements:

            # Skip fully repaid loans
            amount_outstanding = abs(disbursement.loan_request.get_amount_outstanding())

            if amount_outstanding <= 0:
                continue

            """calculate emi"""

            interest = (disbursement.interest_rate/100) / 12


    else:
        print('No disbursement is due today.')

    print('\n===============Script ended===========================\n')
