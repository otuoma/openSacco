from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, FormView, TemplateView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from accounting.models import AccountGroup, Account, AccountTransaction
from accounting.forms import CreateAccountGroupForm, UpdateAccountGroupForm, CreateAccountForm, UpdateAccountForm, CreateTransactionForm, UpdateTransactionForm
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.mixins import PermissionRequiredMixin
from accounting.utils import get_account_balance


class DeleteTransaction(PermissionRequiredMixin, DeleteView):
    model = AccountTransaction
    permission_required = 'accounting.change_accounttransaction'
    raise_exception = True
    success_url = '/accounting/'

    def get_success_url(self):

        messages.success(self.request, 'Transaction has been deleted', extra_tags='alert alert-danger')

        return self.success_url


class UpdateAccountTransaction(PermissionRequiredMixin, FormView):
    permission_required = 'accounting.change_accounttransaction'
    raise_exception = True
    template_name = 'accounting/update_transaction.html'
    form_class = UpdateTransactionForm

    def post(self, request, *args, **kwargs):

        transaction = get_object_or_404(AccountTransaction, pk=self.kwargs['pk'])

        form = self.form_class(data=request.POST, instance=transaction)

        if form.is_valid():

            updated_transaction = form.save(commit=False)
            updated_transaction.staff_id = self.request.user.pk
            updated_transaction.save()

            messages.success(request, 'Success, transaction has been updated', extra_tags='alert alert-success')

            return redirect(to='accounting:update-transaction', pk=self.kwargs['pk'])
        else:
            messages.error(request, 'Failed, form errors occurred', extra_tags='alert alert-danger')

        account = get_object_or_404(Account, pk=transaction.account_id)

        transactions = AccountTransaction.objects.filter(account_id=transaction.account_id)

        context = {
            'account': account,
            'transaction': transaction,
            'transactions': transactions,
            'form': form
        }
        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        transaction = get_object_or_404(AccountTransaction, pk=self.kwargs['pk'])

        form = self.form_class(instance=transaction)

        account = get_object_or_404(Account, pk=transaction.account_id)

        transactions = AccountTransaction.objects.filter(account_id=transaction.account_id)

        context = {
            'account': account,
            'form': form,
            'transaction': transaction,
            'transactions': transactions
        }

        return render(request, self.template_name, context=context)


class RecordAccountTransaction(PermissionRequiredMixin, FormView):
    template_name = 'accounting/record_transactions.html'
    form_class = CreateTransactionForm
    permission_required = 'accounting.add_accounttransaction'
    raise_exception = True

    def post(self, request, *args, **kwargs):

        account = Account.objects.filter(pk=self.kwargs['pk'])

        form = self.form_class(data=request.POST)

        if form.is_valid():

            transaction = form.save(commit=False)
            transaction.account_id = self.kwargs['pk']
            transaction.staff_id = self.request.user.pk
            transaction.save()

            messages.success(request, 'Success, transaction has been recorded', extra_tags='alert alert-success')

            return redirect(to='accounting:record-transaction', pk=self.kwargs['pk'])

        else:

            messages.error(request, 'Error, transaction not recorded', extra_tags='alert alert-danger')

        transactions = AccountTransaction.objects.filter(account_id=self.kwargs['pk'])

        context = {
            'form': form,
            'account': account.get(),
            'transactions': transactions
        }
        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        account = Account.objects.filter(pk=self.kwargs['pk'])

        transactions = AccountTransaction.objects.filter(account_id=self.kwargs['pk'])

        form = self.form_class

        context = {
            'form': form,
            'account': account.get(),
            'transactions': transactions
        }
        return render(request, self.template_name, context=context)


class ViewAccountTransactions(PermissionRequiredMixin, TemplateView):
    template_name = 'accounting/account_transactions.html'
    permission_required = 'accounting.add_accounttransaction'
    raise_exception = True

    def get(self, request, *args, **kwargs):

        account = get_object_or_404(Account, pk=self.kwargs['pk'])

        transactions = AccountTransaction.objects.filter(account_id=self.kwargs['pk'])

        context = {
            'account': account,
            'transactions': transactions,
            'account_sum': transactions.aggregate(Sum('amount'))['amount__sum']
        }
        return render(request, self.template_name, context=context)


class TrialBalance(PermissionRequiredMixin, FormView):
    template_name = 'accounting/trial_balance.html'
    permission_required = 'accounting.add_account'
    raise_exception = True

    def get(self, request, *args, **kwargs):

        account_groups = AccountGroup.objects.all().order_by('group_number')

        groups_list = []
        debit_total = 0
        credit_total = 0

        for group in account_groups:

            group_children = group.get_children()
            children_data = []

            for account in group_children:

                if request.GET.get('status') == 'active' and account.status == 'closed':
                    continue

                if request.GET.get('status') == 'closed' and account.status == 'active':
                    continue

                account_balance = get_account_balance(account, request)

                children_data.append({
                    'account_number': account.account_number,
                    'account_name': account.account_name,
                    'account_balance': account_balance,
                    'increases': account.increases
                })

                if account.increases == 'credit':
                    credit_total += account_balance
                else:
                    debit_total += account_balance

            groups_list.append({
                'group_name': group.group_name,
                'group_number': group.group_number,
                'children_data': children_data
            })

        context = {
            'accounts_dict': groups_list,
            'credit_total': credit_total,
            'debit_total': debit_total
        }

        return render(request, self.template_name, context=context)


class CreateAccount(PermissionRequiredMixin, FormView):
    permission_required = 'accounting.add_account'
    raise_exception = True
    template_name = 'accounting/create_account.html'
    form_class = CreateAccountForm
    success_url = '/accounting/create-account'

    def get(self, request, *args, **kwargs):

        context = {
            'accounts_list': Account.objects.all().order_by('account_number'),
            'form': self.form_class
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():

            account = Account(
                account_number=form.cleaned_data['account_number'],
                account_name=form.cleaned_data['account_name'],
                account_type=form.cleaned_data['account_type'],
                account_group=form.cleaned_data['account_group'],
                opening_balance=form.cleaned_data['opening_balance'],
                opening_date=form.cleaned_data['opening_date'],
                increases=form.cleaned_data['increases'],
                inherits=form.cleaned_data['inherits'],
                description=form.cleaned_data['description']
            )

            account.save()

            messages.success(request, 'Account has been created', extra_tags='alert alert-success')

            return redirect(to='accounting:create-account')

        else:
            messages.error(request, 'Error, account not created', extra_tags='alert alert-danger')

        context = {
            'accounts_list': Account.objects.all().order_by('account_number'),
            'form': self.form_class
        }

        return render(request, self.template_name, context=context)


class DeleteAccount(PermissionRequiredMixin, DeleteView):
    model = Account
    permission_required = 'accounting.change_account'
    raise_exception = True
    success_url = '/accounting/create-account'

    def get_success_url(self):

        messages.success(self.request, 'Account has been deleted', extra_tags='alert alert-danger')

        return self.success_url


class UpdateAccount(PermissionRequiredMixin, FormView):
    permission_required = 'accounting.change_account'
    raise_exception = True
    template_name = 'accounting/update_account.html'
    form_class = UpdateAccountForm

    def get(self, request, *args, **kwargs):

        account = get_object_or_404(Account, pk=self.kwargs['pk'])

        initial = {
            'account_number': account.account_number,
            'account_name': account.account_name,
            'account_group': account.account_group,
            'account_type': account.account_type,
            'increases': account.increases,
            'opening_balance': account.opening_balance,
            'opening_date': account.opening_date,
            'status': account.status,
            'inherits': account.inherits,
            'description': account.description,
        }

        context = {
            'accounts_list': Account.objects.all().order_by('account_number'),
            'form': self.form_class(initial=initial),
            'account': account
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        instance = get_object_or_404(Account, pk=self.kwargs['pk'])

        form = self.form_class(data=request.POST)

        if form.is_valid():

            instance.account_number = form.cleaned_data['account_number']
            instance.account_name = form.cleaned_data['account_name']
            instance.account_type = form.cleaned_data['account_type']
            instance.account_group = form.cleaned_data['account_group']
            instance.opening_balance = form.cleaned_data['opening_balance']
            instance.opening_date = form.cleaned_data['opening_date']
            instance.increases = form.cleaned_data['increases']
            instance.inherits = form.cleaned_data['inherits']
            instance.description = form.cleaned_data['description']

            instance.save()

            messages.success(request, 'Account has been updated', extra_tags='alert alert-success')

            return redirect(to='accounting:update-account', pk=instance.pk)

        else:
            messages.error(request, 'Error, account not updated', extra_tags='alert alert-danger')

        context = {
            'accounts_list': Account.objects.all().order_by('account_number'),
            'form': form,
            'account': instance
        }

        return render(request, self.template_name, context=context)


class ChartOfAccounts(PermissionRequiredMixin, ListView):
    model = AccountGroup
    permission_required = 'accounting.add_accountinggroup'
    raise_exception = True
    template_name = 'accounting/chart_of_accounts.html'
    context_object_name = 'group_list'
    ordering = 'group_number'
    login_url = '/members/login/'

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect(to='members:login')

        account_groups = AccountGroup.objects.all().order_by('group_number')

        groups_list = []

        for group in account_groups:

            group_children = group.get_children()
            children_data = []

            for account in group_children:

                if request.GET.get('status') == 'active' and account.status == 'closed':
                    continue

                if request.GET.get('status') == 'closed' and account.status == 'active':
                    continue

                account_balance = get_account_balance(account, request)

                children_data.append({
                    'account_number': account.account_number,
                    'account_name': account.account_name,
                    'account_balance': account_balance,
                    'inherits': account.inherits,
                    'increases': account.increases,
                    'pk': account.pk
                })

            groups_list.append({
                'group_name': group.group_name,
                'group_number': group.group_number,
                'children_data': children_data
            })

        context = {
            'accounts_dict': groups_list,
        }

        return render(request, self.template_name, context=context)


class DeleteAccountGroup(PermissionRequiredMixin, DeleteView):
    model = AccountGroup
    permission_required = 'accounting.delete_accountgroup'
    raise_exception = True
    success_url = '/accounting/create-account-group/'

    def get_success_url(self):

        messages.success(self.request, 'Group has been deleted', extra_tags='alert alert-success')

        return self.success_url


class UpdateAccountGroup(PermissionRequiredMixin, UpdateView):
    model = AccountGroup
    permission_required = 'accounting.change_accountgroup'
    raise_exception = True
    template_name = 'accounting/update_accountgroup.html'
    form_class = UpdateAccountGroupForm

    def get_success_url(self):

        messages.success(self.request, 'Group has been updated', extra_tags='alert alert-success')

        return '/accounting/create-account-group/'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['accounts_in_group'] = self.model.objects.filter(pk=self.kwargs['pk'])
        return context


class CreateAccountGroup(PermissionRequiredMixin, CreateView):
    model = AccountGroup
    permission_required = 'accounting.add_accountgroup'
    raise_exception = True
    template_name = 'accounting/create_accountgroup.html'

    def post(self, request, *args, **kwargs):

        form = CreateAccountGroupForm(data=request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, new account group created', extra_tags='alert alert-success')
        else:
            messages.error(request, 'Error, account group not created', extra_tags='alert alert-danger')

        context = {
            'form': CreateAccountGroupForm,
            'account_groups': self.model.objects.all().order_by('group_number')
        }

        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        context = {
            'form': CreateAccountGroupForm,
            'account_groups': self.model.objects.all().order_by('group_number')
        }

        return render(request, self.template_name, context=context)



