from django import forms
from payments.models import (PaymentType, Payment,)


class UploadContributionsForm(forms.Form):

    file = forms.FileField(validators='')

    def __init__(self, *args, **kwargs):

        super(UploadContributionsForm, self).__init__(*args, **kwargs)

        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = '.xlsx'

    class Meta:
        model = Payment
        fields = ['file']


class AllPaymentsFiltersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AllPaymentsFiltersForm, self).__init__(*args, **kwargs)
        self.fields['payment_type'].widget.attrs['class'] = 'form-control'
        self.fields['payment_type'].required = False

    class Meta:
        model = Payment
        fields = ('payment_type',)


class UpdatePaymentForm(forms.ModelForm):

    def __init__(self, member, *args, **kwargs):
        super(UpdatePaymentForm, self).__init__(*args, **kwargs)
        self.fields['member'].widget.attrs['class'] = 'form-control'
        self.fields['payment_type'].widget.attrs['class'] = 'form-control'
        # self.fields['paid_by'].widget.attrs['style'] = 'display:none;'
        self.fields['notes'].widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['rows'] = '3'
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'date'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['member'].queryset = member

    class Meta:
        model = Payment
        fields = ('amount', 'member', 'payment_type', 'notes', 'date')


class PaymentForm(forms.ModelForm):
    def __init__(self, member, paid_by, payment_types, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['member'].widget.attrs['class'] = 'form-control'
        self.fields['payment_type'].widget.attrs['class'] = 'form-control'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['paid_by'].widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['rows'] = '3'
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'date'

        self.fields['member'].queryset = member
        self.fields['payment_type'].queryset = payment_types
        self.fields['member'].empty_label = None
        self.fields['paid_by'].queryset = paid_by
        self.fields['paid_by'].empty_label = None

    class Meta:
        model = Payment
        fields = ('member', 'payment_type', 'amount', 'paid_by', 'total', 'date', 'notes',)


class UpdatePaymentTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdatePaymentTypeForm, self).__init__(*args, **kwargs)
        self.fields['payment_type'].widget.attrs['class'] = 'form-control'
        self.fields['frequency'].widget.attrs['class'] = 'form-control'
        self.fields['min_amount'].widget.attrs['class'] = 'form-control'
        self.fields['flag'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = PaymentType
        exclude = ['slug']


class PaymentTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentTypeForm, self).__init__(*args, **kwargs)
        self.fields['payment_type'].widget.attrs['class'] = 'form-control'
        self.fields['frequency'].widget.attrs['class'] = 'form-control'
        self.fields['min_amount'].widget.attrs['class'] = 'form-control'
        self.fields['flag'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = PaymentType
        exclude = ('slug',)






