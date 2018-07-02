from django import forms
from .models import Expenditure
from datetime import datetime


class FilterExpendituresForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FilterExpendituresForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].widget.attrs['class'] = 'form-control'
        self.fields['date_to'].widget.attrs['class'] = 'form-control'
        self.fields['date_from'].widget.attrs['id'] = 'date_from'
        self.fields['date_to'].widget.attrs['id'] = 'date_to'

    date_from = forms.DateTimeField(initial=datetime.today())
    date_to = forms.DateTimeField(initial=datetime.today())


class AddExpenditureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = '1'
        self.fields['description'].widget.attrs['placeholder'] = 'Spent for ..'
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'date'

    class Meta:
        model = Expenditure
        fields = ['amount', 'description', 'date']


class UpdateExpenditureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['rows'] = '1'
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'date'

    class Meta:
        model = Expenditure
        fields = ['amount', 'description', 'date']




