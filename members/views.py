from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (CreateView, TemplateView, FormView, ListView, DetailView, UpdateView)
from members.forms import (RequestPasswordResetForm, SetPermissionsForm, BankAccountForm, ActivateAccountForm, UploadScannedIDForm, PrintMembersForm, SignUpForm, LoginForm, UploadProfilePhotoForm, EditMemberForm, CreatePasswordForm, AdminCreateMemberForm, MemberBulkUploadForm, ChangePasswordForm)
from members.models import Member, BankAccount
from dividends.models import (DividendIssue, DividendDisbursement)
from payments.models import Payment
from loans.models import LoanRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Permission, PermissionDenied
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,)
import pandas as pd
from shares.models import MemberShare, Share
from django.conf import settings
from django.db.models import Sum
from django.core.mail import mail_managers, send_mail
from django.core.exceptions import ValidationError
from django.core.exceptions import (PermissionDenied, ObjectDoesNotExist)
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from easy_pdf.views import PDFTemplateView
from django.contrib.auth.models import Permission
from website.models import Download, FooterRight, FooterLeft, FooterCenter


class ResetRequestedPassword(FormView):
    model = Member
    form_class = CreatePasswordForm
    template_name = 'members/reset_requested_password.html'

    def post(self, request, *args, **kwargs):

        member = get_object_or_404(self.model, email=request.GET.get('email'))

        form = CreatePasswordForm(
            user=member,
            data=request.POST
        )

        if form.is_valid():

            member.set_password(raw_password=form.cleaned_data['new_password2'])

            member.save()

            messages.success(request, 'New password created, login again', extra_tags='alert alert-success')

            try:
                send_mail(
                    subject='Password Changed',
                    message='Your password has just been changed. \nIf you did not make this change, please report the issue immediately. ',
                    from_email='info@wecanyouthsacco.co.ke',
                    recipient_list=[member.email],
                    fail_silently=True
                )
            except Exception:
                pass

            return redirect(to='members:login')
        else:
            context = {
                'member': member,
                'form': form
            }

            messages.error(request, 'Errors occured', extra_tags='alert alert-danger')

            return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        context = {
            'form': RequestPasswordResetForm
        }

        if request.GET.get('token') and request.GET.get('email'):

            try:
                member = self.model.objects.get(email=request.GET.get('email'))

            except ObjectDoesNotExist:
                member = None

            token_generator = PasswordResetTokenGenerator()

            if member is not None and token_generator.check_token(user=member, token=request.GET.get('token')):

                context['form'] = CreatePasswordForm(user=Member)
                context['member'] = member

                messages.info(request, 'Create a new password', extra_tags='alert alert-info')

                return render(request, self.template_name, context=context)
            else:

                messages.error(request, 'Bad token URL', extra_tags='alert alert-danger')

                return render(request, 'members/request_password_reset.html', context=context)

        else:
            messages.error(request, 'Broken token URL', extra_tags='alert alert-danger')

            return render(request, 'members/request_password_reset.html', context=context)


class RequestPasswordReset(FormView):
    model = Member
    template_name = 'members/request_password_reset.html'
    form_class = RequestPasswordResetForm

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():

            try:

                member = self.model.objects.get(email=form.cleaned_data['email'])

            except ObjectDoesNotExist:

                member = None

            if member is None:

                messages.error(request, "Email does not exist here", extra_tags='alert alert-info')
            else:

                #create token
                token_generator = PasswordResetTokenGenerator()

                token = token_generator.make_token(user=member)

                html_msg = "Someone made a request to reset your password."
                html_msg += "<p>If this was you, please "
                html_msg += "<a href='http://wecanyouthsacco.co.ke/members/reset-requested-password/?token={}&email={}' target='_blank'>".format(token, member.email)
                html_msg += "click here</a>.</p> Otherwise, ignore this email but also report to officials.<p>NOTE: This link can be used only once.</a>"

                print(html_msg)

                send_mail(
                    subject="Password reset",
                    message="",
                    html_message=html_msg,
                    recipient_list=[member.email],
                    from_email='wecanys2@gmail.com'
                )

                messages.success(request, "Check your email inbox", extra_tags='alert alert-info')
        else:
            messages.error(request, "Errors occured, form is not valid", extra_tags='alert alert-danger')

        context = {
            'form': form,
        }

        return render(request, self.template_name, context=context)


class SetPermissions(PermissionRequiredMixin, UpdateView):
    model = Member
    template_name = 'members/set-permissions.html'
    permission_required = ['members.change_member']
    permission_denied_message = "Sorry, you dont have permission for this action"
    raise_exception = True

    def get(self, request, *args, **kwargs):

        member = get_object_or_404(Member, pk=self.kwargs['pk'])

        initial = {'user_permissions': Permission.objects.filter(user=member)}

        form = SetPermissionsForm(initial=initial, instance=member)

        context = {
            'form': form,
            'member': member
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        member = get_object_or_404(Member, pk=self.kwargs['pk'])

        form = SetPermissionsForm(data=request.POST, instance=member)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, permissions updated', extra_tags='alert alert-success')

            return redirect(to='members:set-permissions', pk=self.kwargs['pk'])
        else:
            messages.error(request, 'Failed, form errors occurred', extra_tags='alert alert-danger')

            context = {
                'form': form,
                'member': member
            }

            return render(request, self.template_name, context=context)


class EditBankAccount(PermissionRequiredMixin, CreateView):
    model = BankAccount
    template_name = 'members/edit_bank_account.html'
    permission_required = ['members.change_bankaccount']
    permission_denied_message = 'You dont have permission to perform action'
    raise_exception = True

    def post(self, request, *args, **kwargs):

        bank_account = BankAccount.objects.get(pk=self.kwargs['account_id'])

        member = Member.objects.filter(pk=bank_account.member_id)

        form = BankAccountForm(member=member, instance=bank_account, data=request.POST)

        bank_accounts = BankAccount.objects.filter(member_id=bank_account.member_id)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, account was edited', extra_tags='alert alert-success')

            return redirect(to='members:edit-bank-account', account_id=self.kwargs['account_id'])

        else:

            messages.error(request, 'Failed, form errors occured.', extra_tags='alert alert-danger')

            context = {
                'form': form,
                'member': bank_account.member,
                'bank_accounts': bank_accounts
            }

            return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        bank_account = BankAccount.objects.get(pk=self.kwargs['account_id'])

        member = Member.objects.filter(pk=bank_account.member_id)

        form = BankAccountForm(member=member, instance=bank_account)

        bank_accounts = BankAccount.objects.filter(member_id=bank_account.member_id)

        context = {
            'form': form,
            'member': bank_account.member,
            'bank_accounts': bank_accounts,
            'bank_account': bank_account
        }

        return render(request, self.template_name, context=context)

    def has_permission(self):

        account = BankAccount.objects.get(pk=self.kwargs['account_id'])

        if self.request.user.pk == account.member_id:
            return True

        if self.request.user.has_perms(self.permission_required):
            return True


class CreateBankAccount(PermissionRequiredMixin, CreateView):
    model = BankAccount
    template_name = 'members/create_bank_account.html'
    permission_required = ['members.add_bankaccount']
    permission_denied_message = 'You dont have permission to perform action'
    raise_exception = True

    def has_permission(self):

        if self.request.user.pk == self.kwargs['member_id']:
            return True

        if self.request.user.has_perms(self.permission_required):
            return True

    def get(self, request, *args, **kwargs):
        member = Member.objects.filter(pk=self.kwargs['member_id'])

        form = BankAccountForm(member=member)
        bank_accounts = BankAccount.objects.filter(member_id=self.kwargs['member_id'])

        context = {
            'form': form,
            'member': member.get(),
            'bank_accounts': bank_accounts
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        member = Member.objects.filter(pk=self.kwargs['member_id'])

        form = BankAccountForm(member=member, data=request.POST)

        bank_accounts = BankAccount.objects.filter(member_id=self.kwargs['member_id'])

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, account was created', extra_tags='alert alert-success')

            return redirect(to='members:create-bank-account', member_id=self.kwargs['member_id'])

        else:

            messages.error(request, 'Failed, form errors occured.', extra_tags='alert alert-danger')

            context = {
                'form': form,
                'member': member.get(),
                'bank_accounts': bank_accounts
            }

            return render(request, self.template_name, context=context)


class UploadScannedID(FormView):

    def post(self, request, *args, **kwargs):

        form = UploadScannedIDForm(
            files=request.FILES,
            data=request.POST
        )

        if form.is_valid():

            member = get_object_or_404(Member, pk=self.kwargs['pk'])

            member.scanned_id = form.cleaned_data['scanned_id']

            member.save()

            messages.success(request, 'Success, ID saved ..', extra_tags='alert alert-success')

        else:  # Form is not valid

            messages.error(request, 'Failed, errors occured.', extra_tags='alert alert-danger')

        return redirect(to='members:profile', pk=self.kwargs['pk'])


class FilterMembersList(FormView):
    template_name = 'members/filter-members-list.html'
    form_class = PrintMembersForm


class PrintMembersList(PDFTemplateView):
    template_name = 'members/print-members-pdf.html'
    download_filename = 'hello.pdf'

    def get_context_data(self, **kwargs):

        context = super(PrintMembersList, self).get_context_data(**kwargs)

        context['title'] = 'List of Members'
        context['base_url'] = 'http://localhost:8000' + settings.STATIC_URL
        context['registered_from'] = '2000-01-01'
        context['registered_to'] = '2200-12-31'
        context['is_active'] = True
        context['is_staff'] = False
        context['is_superuser'] = False

        if self.request.GET.get('registered_from'):
            context['registered_from'] = self.request.GET.get('registered_from')

        if self.request.GET.get('registered_to'):
            context['registered_to'] = self.request.GET.get('registered_to')

        if self.request.GET.get('is_active') == 'off':
            context['is_active'] = False

        if self.request.GET.get('is_staff') == 'on':
            context['is_staff'] = True

        if self.request.GET.get('is_superuser') == 'on':
            context['is_superuser'] = True

        context['members_list'] = Member.objects.filter(
            date_joined__gte=context['registered_from'],
            date_joined__lte=context['registered_to'],
            is_active=context['is_active'],
            is_staff=context['is_staff'],
            is_superuser=context['is_superuser']
        )

        return context


class BulkMemberUpload(PermissionRequiredMixin, CreateView):
    permission_required = 'Add Member'
    template_name = 'members/create_member.html'
    model = Member
    form_class = AdminCreateMemberForm

    def get(self, request, *args, **kwargs):

        return redirect(to='members:admin-create-member')

    def post(self, request, *args, **kwargs):

        bulk_form = MemberBulkUploadForm(data=request.POST, files=request.FILES)
        members = []

        if bulk_form.is_valid():

            if ".xlsx" not in request.FILES['file'].name:
                raise ValidationError("Filetype is not valid MS excel.")

            df = pd.read_excel(request.FILES['file'])

            fails = 0

            for index, row in df.iterrows():

                try:
                    single_member = Member.objects.create_user(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        phone_number=row['phone_number'],
                        national_id=row['national_id'],
                        member_number=row['member_number'],
                        password=row['password'],
                        is_active=True
                    )

                    single_member.save()

                    members.append(single_member)

                except:

                    fails += 1
        else:

            messages.error(request, 'Failed, errors occred in the form', extra_tags='alert alert-danger')

            fails = ''

        context = {
            'form': self.form_class,
            'members': members,
            'bulk_form': bulk_form
        }

        message = str(len(members)) + ' records uploaded, ' + str(fails) + ' records failed.'

        messages.info(request, message=message, extra_tags='alert alert-info')

        return render(request, self.template_name, context=context)


class ActivateAccount(PermissionRequiredMixin, UpdateView):
    model = Member
    permission_required = 'members.can_change_members'
    raise_exception = True
    permission_denied_message = 'You dont have permission to change member status'
    form_class = ActivateAccountForm

    def post(self, request, *args, **kwargs):

        member = Member.objects.get(pk=self.kwargs['pk'])

        form = ActivateAccountForm(data=request.POST, instance=member)

        if form.is_valid():

            m = form.save(commit=False)
            m.is_active = True
            m.save()

            messages.success(request, 'Success, member status was changed.', extra_tags='alert alert-success')

        else:
            messages.error(request, 'Failed, errors occured in the form', extra_tags='alert alert-danger')

        return redirect(to='members:profile', pk=self.kwargs['pk'])


class DeactivateAccount(PermissionRequiredMixin, UpdateView):
    model = Member
    permission_required = 'members.can_change_members'
    raise_exception = True
    permission_denied_message = 'You dont have permission to change member status'

    def post(self, request, *args, **kwargs):

        member = Member.objects.get(pk=self.kwargs['pk'])

        member.is_active = False

        member.save()

        member.user_permissions.remove(
            Permission.objects.get(codename='request_loan')
        )

        messages.success(request, 'Success, status changed to inactive.', extra_tags='alert alert-success')

        return redirect(to='members:profile', pk=self.kwargs['pk'])


class DeactivateAccounts(PermissionRequiredMixin, UpdateView):
    model = Member
    template_name = ''
    permission_required = 'members.can_change_members'
    raise_exception = True
    permission_denied_message = 'You dont have permission to change member status'

    def post(self, request, *args, **kwargs):

        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied

        members = Member.objects.filter(is_superuser=False).update(is_active=False)

        messages.success(request, str(members) + ' members deactivated.', extra_tags='alert alert-success')

        context = {}

        return render(request, self.template_name, context=context)


class EditMember(UpdateView):
    model = Member
    form_class = EditMemberForm
    template_name = 'members/edit_member.html'

    def post(self, request, *args, **kwargs):

        instance = get_object_or_404(Member, pk=self.kwargs['pk'])

        form = EditMemberForm(data=request.POST, instance=instance)

        if form.is_valid():

            form.save()

            messages.success(request, 'Member details saved', extra_tags='alert alert-success')

            return redirect(to='members:profile', pk=self.kwargs['pk'])
        else:
            messages.error(request, 'Errors occured.', extra_tags='alert alert-danger')

            context = {
                'member': instance,
                'form': form,
            }

            return render(request, self.template_name, context=context)


class UploadProfilePhoto(LoginRequiredMixin, UpdateView):
    template_name = 'members/member_profile.html'
    model = Member

    def post(self, request, *args, **kwargs):

        member = self.model.objects.get(pk=self.kwargs['pk'])

        form = UploadProfilePhotoForm(request.POST, request.FILES, instance=member)

        if form.is_valid():

            form.save()

            messages.error(request, 'Profile photo changed', extra_tags='alert alert-success')

            return redirect(to='members:profile', pk=self.kwargs['pk'])
        else:
            messages.error(request, 'Errors occured, try again', extra_tags='alert alert-danger')

            return redirect(to='members:profile', pk=self.kwargs['pk'])


class MemberProfile(PermissionRequiredMixin, DetailView):
    template_name = 'members/member_profile.html'
    model = Member
    context_object_name = 'member'
    permission_required = 'members.can_view_profiles'
    raise_exception = True
    permission_denied_message = "You dont have permission to view members private profiles"
    login_url = '/members/login/'

    def has_permission(self):

        if self.kwargs['pk'] == self.request.user.pk:
            return True

        if self.request.user.is_staff:
            return True

        if self.request.user.is_superuser:
            return True

    def get_context_data(self, **kwargs):

        member = get_object_or_404(Member, pk=self.kwargs['pk'])
        share = Share.objects.first()

        total_contributions = Payment.objects.filter(
            member_id=self.kwargs['pk'],
            payment_type__flag='contribution'
        ).aggregate(Sum('amount'))

        loans_borrowed = LoanRequest.objects.filter(
            requested_by_id=member.pk
        )

        current_issue = DividendIssue.objects.order_by('id').last()

        try:
            current_issue_id = current_issue.id
        except AttributeError:
            current_issue_id = None

        total_dividends = DividendDisbursement.objects.filter(
            member_id=member.pk,
            dividend_issue=current_issue_id
        ).order_by('date').last()

        if total_dividends is None:
            total_dividends = 0
        else:
            total_dividends = total_dividends.amount

        context = super(MemberProfile, self).get_context_data(**kwargs)

        context['form'] = UploadProfilePhotoForm

        try:
            shares = MemberShare.objects.get(member_id=member.pk)

            context['member_shares'] = shares.quantity

        except MemberShare.DoesNotExist:

            context['member_shares'] = 0

        if share is None:
            share_val = 0
        else:
            share_val = share.share_value

        bank_accounts = BankAccount.objects.filter(
            member_id=member.pk
        )

        context['share_value'] = share_val * context['member_shares']
        context['total_contributions'] = total_contributions
        context['bank_accounts'] = bank_accounts
        context['total_dividends'] = total_dividends
        context['loans_borrowed'] = loans_borrowed

        context['profile_form'] = EditMemberForm(instance=member)

        context['scanned_id_form'] = UploadScannedIDForm
        context['activate_account_form'] = ActivateAccountForm

        if member == self.request.user:

            context['change_password_form'] = ChangePasswordForm(user=self.request.user)
        else:

            context['create_password_form'] = CreatePasswordForm(user=member)

        return context


class MemberDirectory(LoginRequiredMixin, ListView, FormView):
    model = Member
    template_name = 'members/directory.html'
    paginate_by = 20

    def get(self, request, *args, **kwargs):

        if not self.request.user.is_active:
            raise PermissionDenied

        members = Member.objects.all().order_by('-date_joined')

        paginator = Paginator(members, self.paginate_by)

        page = request.GET.get('page', 1)

        try:
            members_list = paginator.page(page)
        except PageNotAnInteger:
            members_list = paginator.page(1)
        except EmptyPage:
            members_list = paginator.page(paginator.num_pages)

        activate_account_form = ActivateAccountForm()

        try:
            context = {
                'total_members': members.count(),
                'active_members': self.model.objects.filter(is_active=True).count(),
                'inactive_members': self.model.objects.filter(is_active=False).count(),
                'staff_members': self.model.objects.filter(is_staff=True).count(),
                'members_list': members_list,
                'activate_account_form': activate_account_form,
            }
            if request.GET.get('list', '') == 'active':
                context['members_list'] = self.model.objects.filter(is_active=True)

            if request.GET.get('list', '') == 'new':
                context['members_list'] = self.model.objects.filter(is_active=False)

            if request.GET.get('list', '') == 'staff':
                context['members_list'] = self.model.objects.filter(is_staff=True)

        except ObjectDoesNotExist:
            context = {}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        if not self.request.user.is_active:
            raise PermissionDenied

        member_number = request.POST.get('member_number', '')

        if member_number == '':
            messages.error(request, 'Error, null member number provided.', extra_tags='alert alert-danger')
            return redirect(to='members:directory')

        try:
            context = {
                'total_members': self.model.objects.all().count(),
                'active_members': self.model.objects.filter(is_active=True).count(),
                'inactive_members': self.model.objects.filter(is_active=False).count(),
                'staff_members': self.model.objects.filter(is_staff=True).count(),
                'members_list': self.model.objects.filter(member_number__exact=member_number)
            }
        except ObjectDoesNotExist:
            raise PermissionDenied

        return render(request, self.template_name, context)


class Welcome(TemplateView):
    template_name = 'members/welcome-page.html'

    def get(self, request, *args, **kwargs):
        context = {
            'download_list': Download.objects.all(),
            'footer_left': FooterLeft.objects.first(),
            'footer_center': FooterCenter.objects.first(),
            'footer_right': FooterRight.objects.first(),
        }

        return render(request, self.template_name, context=context)


class AdminCreateMember(PermissionRequiredMixin, CreateView):
    template_name = 'members/create_member.html'
    model = Member
    permission_required = 'members.can_create_member'
    raise_exception = True
    permission_denied_message = 'You do not have permission to add new members'
    form_class = AdminCreateMemberForm

    def get(self, request, *args, **kwargs):

        last_member = Member.objects.filter(
            member_number__isnull=False
        ).last()

        context = {
            'form': self.form_class,
            'bulk_form': MemberBulkUploadForm,
            'last_member': last_member,
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        self.form_class = AdminCreateMemberForm(data=request.POST)

        if self.form_class.is_valid():

            member = self.form_class.save(commit=False)

            member.is_active = True

            member.set_password(self.form_class.cleaned_data['phone_number'])

            member.save()

            messages.success(request, 'New member has beem created', extra_tags='alert alert-success')

            return redirect(to='members:profile', pk=member.pk)
        else:

            last_member = Member.objects.filter(
                member_number__isnull=False
            ).last()

            context = {
                'form': self.form_class,
                'bulk_form': MemberBulkUploadForm,
                'last_member': last_member,
            }

            messages.error(request, 'Errors occured', extra_tags='alert alert-danger')

            return render(request, self.template_name, context)


class CreateMember(CreateView):
    form_class = SignUpForm
    template_name = 'members/signup.html'

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():

            member = form.save(commit=False)

            member.is_active = False

            member.position = 'member'

            member.save()

            # Send notification to managers and new member
            try:
                managers_html = "%s has requested to join WeCan SACCO" % member.get_full_name()
                managers_html += "<br /> <a href='http://wecanyouthsacco.co.ke/members/profile/%s'>View Details</a>" % member.pk

                mail_managers(
                    subject='New User Registration',
                    message='',
                    html_message=managers_html
                )

                subscriber_html = "Thank you for your interest in joining WeCan Youth SACCO. An official will get in touch for the next steps required for full membership"

                subscriber_html += "<br />If you did not make this request, kindly contact us."

                send_mail(
                    subject='Request received',
                    message='',
                    html_message=subscriber_html,
                    recipient_list=[member.email],
                    from_email='info@wecanyouthsacco.com'
                )
            except Exception:
                pass

            return redirect(to='members:welcome')

        else:
            messages.error(request, 'Errors occured in the form', extra_tags='alert alert-danger')

            return redirect(to='members:create-member')


class ChangePassword(FormView):
    template_name = 'members/member_profile.html'

    def get(self, request, *args, **kwargs):
        return redirect(to='members:profile', pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):

        form = ChangePasswordForm(user=self.request.user, data=request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, 'Password changed, login with new password', extra_tags='alert alert-info')

            return redirect(to='members:login')

        else:

            messages.error(request, 'Errors occured, password not changed', extra_tags='alert alert-danger')

            context = {}

            context['member'] = self.request.user

            context['form'] = UploadProfilePhotoForm

            context['profile_form'] = EditMemberForm(instance=context['member'])

            context['change_password_form'] = ChangePasswordForm(user=self.request.user)

            return render(request, self.template_name, context=context)


class CreatePassword(PermissionRequiredMixin, UpdateView):
    model = Member
    template_name = 'members/create_password.html'
    permission_required = 'members.can_change_member'
    raise_exception = True
    permission_denied_message = "You dont have permission to manage member accounts"

    def get(self, request, *args, **kwargs):

        member = self.model.objects.get(pk=self.kwargs['pk'])

        context = {
            'member': member,
            'profile_photo_form': UploadProfilePhotoForm,
            'create_password_form': CreatePasswordForm(user=member)
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        member = self.model.objects.get(pk=self.kwargs['pk'])

        form = CreatePasswordForm(
            user=member,
            data=request.POST
        )

        if form.is_valid():

            member.set_password(raw_password=form.cleaned_data['new_password2'])

            member.save()

            messages.success(request, 'Success, password set successfully', extra_tags='alert alert-success')

            try:
                send_mail(
                    subject='Password Changed',
                    message='Your password has just been updated. \nIf you did not make this request, please contact the system admin. ',
                    from_email='info@wecanyouthsacco.co.ke',
                    recipient_list=[member.email],
                    fail_silently=True
                )
            except Exception:
                pass

            return redirect(to='members:profile', pk=self.kwargs['pk'])
        else:
            context = {
                'member': member,
                'profile_photo_form': UploadProfilePhotoForm,
                'create_password_form': form
            }

            messages.error(request, 'Errors occured', extra_tags='alert alert-danger')

            return render(request, self.template_name, context=context)


class Login(FormView):
    form_class = LoginForm
    template_name = 'members/login.html'

    def get(self, request, *args, **kwargs):

        if request.GET.get('next'):
            next_url = request.GET.get('next', '/members/')
        else:
            next_url = '/members/'

        context = {
            'next': next_url,
            'form': self.form_class
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        self.form_class = LoginForm(data=request.POST)

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)

        if user is None:

            messages.error(request, 'Error, wrong email or password', extra_tags='alert alert-danger')

            return render(request, self.template_name, {'form': self.form_class})

        else:  # login success

            login(request, user)

            if request.GET.get('next'):

                return redirect(to=request.GET.get('next'))
            else:

                return redirect(to='members:profile', pk=self.request.user.pk)


class Logout(FormView):
    form_class = LoginForm
    template_name = 'members/login.html'

    def get(self, request, *args, **kwargs):

        logout(request)

        return redirect(to='home')
