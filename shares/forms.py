from shares.models import Share, MemberShare
from django import forms


class AddSharesForm(forms.ModelForm):

    def __init__(self, member, *args, **kwargs):

        super(AddSharesForm, self).__init__(*args, **kwargs)

        self.fields['member'].queryset = member
        self.fields['member'].widget.attrs['class'] = 'form-control'
        self.fields['quantity'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = MemberShare
        fields = ['member', 'quantity']


class SetupSharesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SetupSharesForm, self).__init__(*args, **kwargs)
        self.fields['share_value'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Share
        fields = ['share_value']
