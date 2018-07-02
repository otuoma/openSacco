from .models import (DividendIssue, DividendDisbursement)
from django import forms


class UpdateDividendIssueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateDividendIssueForm, self).__init__(*args, **kwargs)
        self.fields['issue_name'].widget.attrs['class'] = 'form-control'
        self.fields['period'].widget.attrs['class'] = 'form-control'
        self.fields['date_effective'].widget.attrs['class'] = 'form-control'
        self.fields['percentage'].widget.attrs['class'] = 'form-control'
        self.fields['percentage'].widget.attrs['step'] = '0.1'
        self.fields['percentage'].widget.attrs['min'] = '0'
        self.fields['date_effective'].widget.attrs['id'] = 'date'
        self.fields['notes'].widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['rows'] = '2'

    class Meta:
        model = DividendIssue
        fields = ('issue_name', 'period', 'date_effective', 'notes', 'percentage',)


class CreateDividendIssueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateDividendIssueForm, self).__init__(*args, **kwargs)
        self.fields['issue_name'].widget.attrs['class'] = 'form-control'
        self.fields['period'].widget.attrs['class'] = 'form-control'
        self.fields['date_effective'].widget.attrs['class'] = 'form-control'
        self.fields['date_effective'].widget.attrs['id'] = 'date'
        self.fields['percentage'].widget.attrs['class'] = 'form-control'
        self.fields['percentage'].widget.attrs['step'] = '0.1'
        self.fields['percentage'].widget.attrs['min'] = '0'
        self.fields['notes'].widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['rows'] = '2'

    class Meta:
        model = DividendIssue
        fields = ('issue_name', 'period', 'date_effective', 'percentage', 'notes',)








