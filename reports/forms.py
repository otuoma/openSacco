from django import forms
from datetime import datetime


class FilterTrialBalanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FilterTrialBalanceForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].widget.attrs['class'] = 'form-control'
        self.fields['date_to'].widget.attrs['class'] = 'form-control'
        self.fields['date_from'].widget.attrs['id'] = 'date_from'
        self.fields['date_to'].widget.attrs['id'] = 'date_to'

    date_from = forms.DateTimeField(initial=datetime.today())
    date_to = forms.DateTimeField(initial=datetime.today())