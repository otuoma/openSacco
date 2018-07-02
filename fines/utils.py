from django.db.models import Sum


def Amount_outstanding(fines):
    total_credit = fines.aggregate(Sum('credit'))
    total_credit = total_credit['credit__sum']

    total_debit = fines.aggregate(Sum('debit'))
    total_debit = total_debit['debit__sum']

    if total_credit is None:
        total_credit = 0.0

    if total_debit is None:
        total_debit = 0.0

    return total_debit - total_credit





