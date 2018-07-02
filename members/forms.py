from django import forms
from django.contrib.auth.forms import (PasswordResetForm, AuthenticationForm, SetPasswordForm, PasswordChangeForm, )
from members.models import Member, BankAccount


class RequestPasswordResetForm(forms.Form):

    email = forms.EmailField(max_length=150, required=True)

    def __init__(self, *args, **kwargs):
        super(RequestPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'


class SetPermissionsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SetPermissionsForm, self).__init__(*args, **kwargs)
        self.fields['user_permissions'].widget.attrs['class'] = 'form-control'
        self.fields['user_permissions'].widget.attrs['size'] = 30

    class Meta:
        model = Member
        fields = ['user_permissions', ]


class EditBankAccountForm(forms.ModelForm):

    def __init__(self, member,  *args, **kwargs):
        super(EditBankAccountForm, self).__init__(*args, **kwargs)
        self.fields['bank'].widget.attrs['class'] = 'form-control'
        self.fields['account_name'].widget.attrs['class'] = 'form-control'
        self.fields['account_number'].widget.attrs['class'] = 'form-control'
        self.fields['branch'].widget.attrs['class'] = 'form-control'
        self.fields['member'].widget.attrs['class'] = 'form-control'
        self.fields['member'].widget.attrs['value'] = member.get().pk
        self.fields['member'].queryset = member

    class Meta:
        model = BankAccount
        fields = '__all__'


class BankAccountForm(forms.ModelForm):

    def __init__(self, member,  *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)
        self.fields['bank'].widget.attrs['class'] = 'form-control'
        self.fields['account_name'].widget.attrs['class'] = 'form-control'
        self.fields['account_number'].widget.attrs['class'] = 'form-control'
        self.fields['branch'].widget.attrs['class'] = 'form-control'
        self.fields['member'].widget.attrs['class'] = 'form-control'
        self.fields['member'].widget.attrs['value'] = member.get().pk
        self.fields['member'].queryset = member

    class Meta:
        model = BankAccount
        fields = '__all__'


class ActivateAccountForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ActivateAccountForm, self).__init__(*args, **kwargs)
        self.fields['member_number'].widget.attrs['class'] = 'form-control'

    member_number = forms.CharField(required=True)

    class Meta:
        model = Member
        fields = ('member_number',)


class UploadScannedIDForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UploadScannedIDForm, self).__init__(*args, **kwargs)
        self.fields['scanned_id'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Member
        fields = ('scanned_id',)


class PrintMembersForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(PrintMembersForm, self).__init__(*args, **kwargs)
        self.fields['registered_from'].widget.attrs['class'] = 'form-control'
        self.fields['registered_to'].widget.attrs['class'] = 'form-control'
        self.fields['registered_from'].widget.attrs['id'] = 'date_from'
        self.fields['registered_to'].widget.attrs['id'] = 'date_to'

    registered_from = forms.DateTimeField(required=False,)
    registered_to = forms.DateTimeField(required=False)
    is_active = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)
    is_staff = forms.BooleanField(required=False)


class MemberBulkUploadForm(forms.Form):
    file = forms.FileField(validators='')

    def __init__(self, *args, **kwargs):
        super(MemberBulkUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = '.xlsx'

    class Meta:
        model = Member
        fields = ('file')


class ResetPasswordForm(PasswordResetForm):
    def __init__(self, user, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields[''].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].widget.attrs['autofocus'] = False

    class Meta:
        # model = Member
        fields = ("email", "for ",)


class ChangePasswordForm(PasswordChangeForm):

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].widget.attrs['autofocus'] = False

    class Meta:
        model = Member
        fields = ("old_password", "new_password1", "new_password2",)


class CreatePasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(CreatePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Member
        fields = ("new_password1", "new_password2")


class EditMemberForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditMemberForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'

        self.fields['last_name'].widget.attrs['class'] = 'form-control'

        self.fields['email'].widget.attrs['class'] = 'form-control'

        self.fields['phone_number'].widget.attrs['class'] = 'form-control'

        self.fields['nationality'].widget.attrs['class'] = 'form-control'

        self.fields['national_id'].widget.attrs['class'] = 'form-control'

        self.fields['dob'].widget.attrs['class'] = 'form-control'

        self.fields['dob'].widget.attrs['id'] = 'date'

        self.fields['postal_address'].widget.attrs['class'] = 'form-control'

        self.fields['city'].widget.attrs['class'] = 'form-control'

        self.fields['house'].widget.attrs['class'] = 'form-control'

        self.fields['street'].widget.attrs['class'] = 'form-control'

        self.fields['occupation'].widget.attrs['class'] = 'form-control'

        self.fields['employer'].widget.attrs['class'] = 'form-control'

        self.fields['marital_status'].widget.attrs['class'] = 'form-control'

        # self.fields['profile_photo'].widget.attrs['class'] = 'form-control'


    class Meta:
        model = Member
        fields = '__all__'
        exclude = ('pk', 'is_superuser', 'is_active', 'is_staff', 'password', 'last_login', 'date_joined', 'member_number', 'username', 'profile_photo', 'scanned_id', 'groups', 'user_permissions', 'email_confirmed')
            # ('first_name', 'last_name', 'email', 'phone_number', 'national_id')


class UploadProfilePhotoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UploadProfilePhotoForm, self).__init__(*args, **kwargs)
        self.fields['profile_photo'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Member
        fields = ("profile_photo",)


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Member
        fields = ("username", "password")


class AdminCreateMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCreateMemberForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'
        self.fields['national_id'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'national_id')


class SignUpForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'email', 'phone_number',)
