from django.db import models
from members.models import Member


class DividendIssue(models.Model):
    """A dividends issue is created once every year or each time the society is issuing dividends"""
    issue_name = models.CharField(max_length=200, null=False, blank=False)
    period = models.CharField(max_length=500, verbose_name='Issue for the period')
    date_effective = models.DateTimeField(
        verbose_name="Date effective.",
        help_text="Members balance as at this date is used to calculate dividends."
    )
    percentage = models.FloatField(max_length=50, null=False, default=5.0)
    notes = models.TextField(max_length=500, blank=True)

    class Meta:
        permissions = (
            ("view_dividend_issues", "Can see available issues"),
        )


class DividendDisbursement(models.Model):
    dividend_issue = models.ForeignKey(DividendIssue, verbose_name='Dividend Issue', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, verbose_name='Member', on_delete=models.CASCADE)
    amount = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True,)

    class Meta:
        permissions = (
            ("view_dividend_disbursements", "Can see dividend disbursements"),
        )

