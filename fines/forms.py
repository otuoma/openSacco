from django import forms
from fines.models import Fine


class PayFineForm(forms.ModelForm):

    def __init__(self, member_account, *args, **kwargs):
        super(PayFineForm, self).__init__(*args, **kwargs)
        self.fields['member_account'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['credit'].widget.attrs['class'] = 'form-control'

        self.fields['member_account'].queryset = member_account

    class Meta:
        model = Fine
        fields = ("member_account", "credit", "description")


class UpdateFineForm(forms.ModelForm):

    def __init__(self, member_account, *args, **kwargs):
        super(UpdateFineForm, self).__init__(*args, **kwargs)
        self.fields['member_account'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['debit'].widget.attrs['class'] = 'form-control'

        self.fields['member_account'].queryset = member_account

    class Meta:
        model = Fine
        fields = ("member_account", "debit", "description")


class CreateFineForm(forms.ModelForm):

    def __init__(self, member_account, *args, **kwargs):
        super(CreateFineForm, self).__init__(*args, **kwargs)
        self.fields['member_account'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['debit'].widget.attrs['class'] = 'form-control'

        self.fields['member_account'].queryset = member_account

    class Meta:
        model = Fine
        fields = ("member_account", "debit", "description")