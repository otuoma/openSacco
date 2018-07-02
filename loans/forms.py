from django import (forms,)
from django.utils.translation import ugettext_lazy as _
from .models import (Loan, LoanRequest, Disbursement, LoanRepayment, Guarantor)


class ArmotizedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ArmotizedForm, self).__init__(*args, **kwargs)
        self.fields['loan_amount'].widget.attrs['class'] = 'form-control'
        self.fields['term'].widget.attrs['class'] = 'form-control'
        self.fields['interest_rate'].widget.attrs['class'] = 'form-control'
        self.fields['type'].widget.attrs['class'] = 'form-control'

    TYPE_CHOICES = (
        ('reducing_balance', 'Reducing balance'),
        ('flat_rate', 'Flat rate'),
    )

    type = forms.ChoiceField(choices=TYPE_CHOICES)
    loan_amount = forms.FloatField(required=True)
    term = forms.IntegerField(required=True, help_text='Repayment period in months')
    interest_rate = forms.IntegerField(required=True)


class ApproveGuaranteeRequestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ApproveGuaranteeRequestForm, self).__init__(*args, **kwargs)

        self.fields['choice'].widget.attrs['class'] = 'form-control'
        self.fields['response_message'].widget.attrs['class'] = 'form-control'
        self.fields['response_message'].widget.attrs['rows'] = '3'

    choice = forms.CharField(
        max_length=50,
        widget=forms.Select(
            choices=(
                ('approved', _('Approve')),
                ('rejected', _('Reject')),
            ),
        ),
    )
    response_message = forms.CharField(widget=forms.Textarea, required=False)


class RequestGuarantorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RequestGuarantorForm, self).__init__(*args, **kwargs)

        self.fields['amount'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Guarantor
        fields = ['amount']


class LoanRepaymentFiltersForm(forms.ModelForm):

    def __init__(self, requested_by, *args, **kwargs):
        super(LoanRepaymentFiltersForm, self).__init__(*args, **kwargs)

        self.fields['loan_request'].queryset = LoanRequest.objects.filter(
            requested_by=requested_by
        )

    class Meta:
        model = LoanRepayment
        fields = ('loan_request',)


class LoanRepaymentForm(forms.ModelForm):
    def __init__(self, loan_request, emi, *args, **kwargs):
        super(LoanRepaymentForm, self).__init__(*args, **kwargs)
        self.fields['loan_request'].widget.attrs['class'] = 'form-control'
        self.fields['credit'].widget.attrs['class'] = 'form-control'
        self.fields['credit'].widget.attrs['id'] = 'amountPaid'
        self.fields['credit'].widget.attrs['step'] = '0.01'
        self.fields['credit'].widget.attrs['placeholder'] = emi
        self.fields['loan_request'].queryset = loan_request
        # self.fields['credit'].queryset = loan_request

    class Meta:
        model = LoanRepayment
        fields = ('loan_request', 'credit',)


class UpdateLoanRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateLoanRequestForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LoanRequest
        fields = ('status', )


class DisbursementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DisbursementForm, self).__init__(*args, **kwargs)

        self.fields['amount_disbursed'].widget.attrs['class'] = 'form-control'
        self.fields['first_due'].widget.attrs['class'] = 'form-control'
        self.fields['first_due'].help_text = 'By default, 45 calendar days from today'
        self.fields['processing_fee'].widget.attrs['class'] = 'form-control'
        self.fields['first_due'].widget.attrs['id'] = 'date'
        self.fields['interest_rate'].widget.attrs['class'] = 'form-control'
        self.fields['interest_on'].widget.attrs['class'] = 'form-control'
        self.fields['repayment_period_unit'].widget.attrs['class'] = 'form-control'
        self.fields['repayment_period'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Disbursement
        fields = ('processing_fee', 'amount_disbursed', 'interest_rate', 'interest_on','repayment_period', 'repayment_period_unit', 'first_due')


class LoanApprovalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LoanApprovalForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = LoanRequest
        fields = ('status',)


class LoanApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LoanApplicationForm, self).__init__(*args, **kwargs)

        self.fields['amount_requested'].widget.attrs['class'] = 'form-control'
        self.fields['loan'].widget.attrs['class'] = 'form-control'
        self.fields['details'].widget.attrs['class'] = 'form-control'
        self.fields['details'].widget.attrs['rows'] = '3'

        # self.fields['requested_by'].queryset = requested_by

    class Meta:
        model = LoanRequest
        fields = ('amount_requested', 'loan', 'details',)


class CreateLoanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateLoanForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['min_amount'].widget.attrs['class'] = 'form-control'
        self.fields['max_amount'].widget.attrs['class'] = 'form-control'
        self.fields['repayment_period'].widget.attrs['class'] = 'form-control'
        self.fields['repayment_period_unit'].widget.attrs['class'] = 'form-control'
        self.fields['interest_rate'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = '3'

    class Meta:
        model = Loan
        fields = ('name', 'min_amount', 'max_amount', 'interest_rate', 'repayment_period', 'repayment_period_unit', 'description',)


class UpdateLoanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateLoanForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['min_amount'].widget.attrs['class'] = 'form-control'
        self.fields['max_amount'].widget.attrs['class'] = 'form-control'
        self.fields['repayment_period'].widget.attrs['class'] = 'form-control'
        self.fields['repayment_period_unit'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = '3'
        self.fields['interest_rate'].widget.attrs['step'] = '0.1'
        self.fields['interest_rate'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Loan
        fields = ('name', 'min_amount', 'max_amount', 'interest_rate', 'repayment_period', 'repayment_period_unit', 'description',)





