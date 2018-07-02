from accounting.models import Account, AccountGroup, BuiltInAccount, AccountTransaction
from django import forms
from django.utils import timezone
from accounting.utils import builtin_accounts


class UpdateTransactionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UpdateTransactionForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'date'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['narration'].widget.attrs['class'] = 'form-control'
        self.fields['narration'].widget.attrs['rows'] = '1'

    class Meta:
        model = AccountTransaction
        exclude = ['member', 'staff', 'account']


class CreateTransactionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateTransactionForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'date'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['narration'].widget.attrs['class'] = 'form-control'
        self.fields['narration'].widget.attrs['rows'] = '1'

    class Meta:
        model = AccountTransaction
        exclude = ['member', 'staff', 'account']


class UpdateAccountForm(forms.Form):
    account_number = forms.CharField(max_length=25, )
    account_name = forms.CharField(max_length=250)
    account_group = forms.ModelChoiceField(queryset=AccountGroup.objects.all().order_by('group_number'))
    account_type = forms.ChoiceField(
        choices=(
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('expense', 'Expense'),
            ('equity', 'Equity'),
            ('revenue', 'Revenue'),
            ('other_account', 'Other Account'),
        ),
        initial='liability'
    )
    increases = forms.ChoiceField(
        choices=(
            ('debit', 'Debit'),
            ('credit', 'Credit'),
        )
    )
    opening_balance = forms.FloatField()
    opening_date = forms.DateField(initial=timezone.datetime.now)
    status = forms.ChoiceField(choices=(
        ('all', '--'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ))
    inherits = forms.ChoiceField(
        choices=builtin_accounts,
        initial='none'
    )
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateAccountForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['account_number'].widget.attrs['class'] = 'form-control'
        self.fields['account_name'].widget.attrs['class'] = 'form-control'
        self.fields['account_group'].widget.attrs['class'] = 'form-control'
        self.fields['account_type'].widget.attrs['class'] = 'form-control'
        self.fields['increases'].widget.attrs['class'] = 'form-control'
        self.fields['opening_balance'].widget.attrs['class'] = 'form-control'
        self.fields['opening_date'].widget.attrs['class'] = 'form-control'
        self.fields['opening_date'].widget.attrs['id'] = 'date'
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['inherits'].widget.attrs['class'] = 'form-control'

        self.fields['inherits'].queryset = BuiltInAccount.objects.all()

        self.fields['description'].widget.attrs['rows'] = 1


class CreateAccountForm(forms.Form):
    account_number = forms.CharField(max_length=25,)
    account_name = forms.CharField(max_length=250)
    account_group = forms.ModelChoiceField(queryset=AccountGroup.objects.all().order_by('group_number'))
    account_type = forms.ChoiceField(
        choices=(
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('expense', 'Expense'),
            ('equity', 'Equity'),
            ('revenue', 'Revenue'),
            ('other_account', 'Other Account'),
        ),
        initial='liability'
    )
    increases = forms.ChoiceField(
        choices=(
            ('debit', 'Debit'),
            ('credit', 'Credit'),
        )
    )
    opening_balance = forms.FloatField()
    opening_date = forms.DateField(initial=timezone.datetime.now)
    status = forms.ChoiceField(
        choices=(
            ('active', 'Active'),
            ('closed', 'Closed'),
        ),
    )
    inherits = forms.ChoiceField(
        choices=builtin_accounts,
        initial='none'
    )
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['account_number'].widget.attrs['class'] = 'form-control'
        self.fields['account_name'].widget.attrs['class'] = 'form-control'
        self.fields['account_group'].widget.attrs['class'] = 'form-control'
        self.fields['account_type'].widget.attrs['class'] = 'form-control'
        self.fields['increases'].widget.attrs['class'] = 'form-control'
        self.fields['opening_balance'].widget.attrs['class'] = 'form-control'
        self.fields['opening_date'].widget.attrs['class'] = 'form-control'
        self.fields['opening_date'].widget.attrs['id'] = 'date'
        self.fields['status'].widget.attrs['class'] = 'form-control'
        self.fields['inherits'].widget.attrs['class'] = 'form-control'

        self.fields['inherits'].queryset = BuiltInAccount.objects.all()

        self.fields['description'].widget.attrs['rows'] = 1


class UpdateAccountGroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UpdateAccountGroupForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['group_number'].widget.attrs['class'] = 'form-control'
        self.fields['group_name'].widget.attrs['class'] = 'form-control'

        self.fields['description'].widget.attrs['rows'] = 1

    class Meta:
        model = AccountGroup
        fields = '__all__'


class CreateAccountGroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CreateAccountGroupForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['group_number'].widget.attrs['class'] = 'form-control'
        self.fields['group_name'].widget.attrs['class'] = 'form-control'

        self.fields['description'].widget.attrs['rows'] = 1

    class Meta:
        model = AccountGroup
        fields = '__all__'


class ChartOfAccountsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ChartOfAccountsForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['account_number'].widget.attrs['class'] = 'form-control'
        self.fields['account_name'].widget.attrs['class'] = 'form-control'
        self.fields['account_type'].widget.attrs['class'] = 'form-control'

        self.fields['description'].widget.attrs['rows'] = 1

    class Meta:
        model = Account
        fields = '__all__'





