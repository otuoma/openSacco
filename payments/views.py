from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (DeleteView, CreateView, ListView, UpdateView, FormView,)
from payments.models import (PaymentType, Payment)
from payments.forms import (UpdatePaymentForm, PaymentTypeForm, UpdatePaymentTypeForm, PaymentForm, AllPaymentsFiltersForm, UploadContributionsForm,)
from django.contrib import messages
from members.models import Member
from datetime import datetime
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import pandas as pd
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from reports.models import TrialBalance
from easy_pdf.views import PDFTemplateView
from django.db.models import Sum
from django.contrib.auth import (PermissionDenied,)
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,)
from accounting.models import Account, AccountGroup, BuiltInAccount
import random


class PrintStatement(PDFTemplateView):
    permission_denied_message = 'You dont have permission to print member statement'
    raise_exception = True
    permission_required = 'payments:view_payments'
    template_name = 'payments/print-statement-pdf.html'

    def get_context_data(self, **kwargs):

        context = super(PrintStatement, self).get_context_data(**kwargs)

        member = get_object_or_404(Member, pk=self.kwargs['pk'])

        context['title'] = 'Payments statement : ' + member.get_full_name()

        date_from = '2000-01-01 00:00:00'
        date_to = '2100-12-31 23:59:59'

        if self.request.GET.get('date_from'):
            date_from = self.request.GET.get('date_from')

        if self.request.GET.get('date_to'):
            date_to = self.request.GET.get('date_to')

        if self.request.GET.get('payment_type'):

            context['contributions'] = Payment.objects.filter(
                payment_type=self.request.GET.get('payment_type'),
                date__gte=date_from + ' 00:00:00',
                date__lte=date_to + ' 23:59:59',
                member_id=self.kwargs['pk']
            )
        else:
            context['contributions'] = Payment.objects.filter(
                date__gte=date_from + ' 00:00:00',
                member_id=self.kwargs['pk'],
                date__lte=date_to + ' 23:59:59'
            )

        return context


class PrintContributions(PDFTemplateView):
    permission_denied_message = 'You dont have permission to print contributions list'
    raise_exception = True
    permission_required = 'payments:view_payments'
    template_name = 'payments/print-payments-pdf.html'

    def get_context_data(self, **kwargs):

        context = super(PrintContributions, self).get_context_data(**kwargs)

        context['title'] = 'Payments statement'

        date_from = '2000-01-01 00:00:00'
        date_to = '2100-12-31 23:59:59'

        if self.request.GET.get('date_from'):
            date_from = self.request.GET.get('date_from')

        if self.request.GET.get('date_to'):
            date_to = self.request.GET.get('date_to')

        if self.request.GET.get('payment_type'):

            context['contributions'] = Payment.objects.filter(
                payment_type=self.request.GET.get('payment_type'),
                date__gte=date_from + ' 00:00:00',
                date__lte=date_to + ' 23:59:59'
            )
        else:
            context['contributions'] = Payment.objects.filter(
                date__gte=date_from + ' 00:00:00',
                date__lte=date_to + ' 23:59:59'
            )

        return context


class UploadContributions(PermissionRequiredMixin, CreateView):
    model = Payment
    permission_required = 'Add Payment'
    raise_exception = True
    permission_denied_message = 'You dont have permission to Upload contributions'
    template_name = 'payments/upload-contributions.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, {'form': UploadContributionsForm})

    def post(self, request, *args, **kwargs):

        form = UploadContributionsForm(data=request.POST, files=request.FILES)
        payments = []
        fails = 0
        exceptions = []

        if form.is_valid():

            if ".xlsx" not in request.FILES['file'].name:
                raise ValidationError("Filetype is not valid MS excel.")

            df = pd.read_excel(request.FILES['file'])

            for index, row in df.iterrows():

                try:
                    payment_type = PaymentType.objects.get(pk=row['payment_code'])

                except ObjectDoesNotExist as exp:

                    exceptions.append(

                        str(row['payment_code']) + " : " + str(exp)
                    )
                    continue

                try:
                    member = Member.objects.get(member_number=row['member_number'])
                except ObjectDoesNotExist as exp:
                    exceptions.append(
                        str(row['member_number']) + " : " + str(exp)
                    )
                    continue

                if payment_type.flag == 'contribution':

                    total = float(member.member_total_contributions()) + float(row['amount'])

                else:
                    total = float(row['amount'])

                try:
                    single_payment = Payment(
                        amount=row['amount'],
                        member=member,
                        payment_type=payment_type,
                        paid_by_id=self.request.user.pk,
                        date=pd.to_datetime(row['date']),
                        total=total
                    )

                    single_payment.save()

                    trial_balance = TrialBalance(
                        credit=row['amount'],
                        timestamp=single_payment.date,
                        debit=0.0,
                        module='Contributions',
                        member=member,
                        staff=self.request.user.get_full_name(),
                        description=payment_type
                    )

                    trial_balance.save()

                    payments.append(single_payment)

                except Exception as exp:

                    exceptions.append(exp)

                    fails += 1
        else:

            messages.error(request, 'Errors occured', extra_tags='alert alert-danger')
        #
        context = {
            'form': form,
            'fails': fails,
            'exceptions': exceptions,
            'payments': payments,
        }
        return render(request, self.template_name, context=context)


class UpdatePayment(PermissionRequiredMixin, UpdateView):
    model = Payment
    permission_required = 'payments.change_payment'
    template_name = 'payments/update-payment.html'

    def get(self, request, *args, **kwargs):

        payment = get_object_or_404(Payment, pk=self.kwargs['pk'])

        member = Member.objects.filter(pk=payment.member.id)

        initial = {
            'member': member.get(),
            'amount': payment.amount,
            'date': payment.date,
            'paid_by': self.request.user,
            'payment_type': payment.payment_type,
            'notes': payment.notes
        }

        context = {
            'form': UpdatePaymentForm(member=member, initial=initial)
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        payment = get_object_or_404(Payment, pk=self.kwargs['pk'])

        member = Member.objects.filter(pk=payment.member.id)

        form = UpdatePaymentForm(member=member, data=request.POST, instance=payment)

        if form.is_valid():

            pay = form.save(commit=False)

            pay.paid_by_id = self.request.user.pk

            pay.save()

            messages.success(request, 'Sucess, payment updated', extra_tags='alert alert-success')

            return redirect(to='payments:statement', pk=member.get().pk)
        else:
            messages.error(request, 'Failed, errors occured', extra_tags='alert alert-danger')

            context = {
                'form': form
            }

            return render(request, self.template_name, context=context)


class MakePayment(PermissionRequiredMixin, CreateView):
    model = Payment
    template_name = 'payments/make-payment.html'
    form_class = PaymentForm
    permission_required = 'payments.add_payment'
    raise_exception = True
    permission_denied_message = 'You dont have permission to access this page'

    def get(self, request, *args, **kwargs):

        member = Member.objects.filter(pk=self.kwargs['pk'])
        paid_by = Member.objects.filter(pk=self.request.user.pk)

        payment = Payment.objects.filter(member=self.kwargs['pk']).last()

        payment_types = PaymentType.objects.filter(is_active=True)

        if not payment:
            last_total = 0
        else:
            last_total = payment.total

        initial = {'total': last_total}

        self.form_class = PaymentForm(member=member, paid_by=paid_by, payment_types=payment_types, initial=initial)

        context = {
            'form': self.form_class,
            'upload_form': UploadContributionsForm,
            'member': member.get()
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        member = Member.objects.filter(pk=self.kwargs['pk'])
        paid_by = Member.objects.filter(pk=self.request.user.pk)

        payment_types = PaymentType.objects.filter(is_active=True)

        form = PaymentForm(data=request.POST, member=member, paid_by=paid_by, payment_types=payment_types)

        if form.is_valid():

            if form.cleaned_data['payment_type'].flag == 'contribution':

                total = float(form.cleaned_data['total']) + float(form.cleaned_data['amount'])

            else:
                total = float(form.cleaned_data['total'])

            payment = Payment(
                member=form.cleaned_data['member'],
                amount=form.cleaned_data['amount'],
                paid_by=form.cleaned_data['paid_by'],
                notes=form.cleaned_data['notes'],
                payment_type=form.cleaned_data['payment_type'],
                total=total,
                date=form.cleaned_data['date']
            )

            payment.save()

            trial_balance = TrialBalance(
                credit=form.cleaned_data['amount'],
                debit=0.0,
                timestamp=form.cleaned_data['date'],
                module='Contributions',
                member=form.cleaned_data['member'],
                staff=self.request.user.get_full_name(),
                description=form.cleaned_data['payment_type']
            )

            trial_balance.save()

            messages.success(request, 'Success, payment has been made', extra_tags='alert alert-success')

            return redirect(to='payments:statement', pk=self.kwargs['pk'])
        else:
            messages.error(request, 'Error, payment not made', extra_tags='alert alert-danger')
            return render(request, self.template_name, {'form': form, 'member': member.get(), 'total': request.POST['total']})


class Statement(LoginRequiredMixin, ListView, FormView):
    model = Payment
    template_name = 'payments/statement.html'
    paginate_by = 15

    def get(self, request, *args, **kwargs):

        member = Member.objects.get(pk=self.kwargs['pk'])

        if not (self.request.user.is_superuser or self.request.user.is_staff or (self.request.user == member)):
            raise PermissionDenied

        queryset = self.model.objects.filter(
            member_id=self.kwargs['pk']
        ).order_by('-date')

        paginator = Paginator(queryset, self.paginate_by)

        page = request.GET.get('page', 1)

        try:
            contributions = paginator.page(page)
        except PageNotAnInteger:
            contributions = paginator.page(1)
        except EmptyPage:
            contributions = paginator.page(paginator.num_pages)

        total_payments = queryset.aggregate(Sum('amount'))
        total_contributions = Payment.objects.filter(
            member_id=self.kwargs['pk'],
            payment_type__flag='contribution'
        ).aggregate(Sum('amount'))

        total_loans_repaid = Payment.objects.filter(
            member_id=self.kwargs['pk'],
            payment_type__flag='loan_repayment'
        ).aggregate(Sum('amount'))

        context = {
            'statement': contributions,
            'member': member,
            'total_payments': total_payments,
            'total_contributions': total_contributions,
            'total_loans_repaid': total_loans_repaid,
            'filters_form': AllPaymentsFiltersForm
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        if not self.request.POST['payment_type'] or not self.request.POST['date_from'] or not self.request.POST['date_to']:
            messages.error(request, 'Error, required value(s) missing ...', extra_tags='alert alert-danger')
            return render(request, self.template_name, {'filters_form': AllPaymentsFiltersForm})

        member = Member.objects.get(pk=self.kwargs['pk'])

        if not (self.request.user.is_superuser or self.request.user.is_staff or (self.request.user == member)):
            raise PermissionDenied

        queryset = self.model.objects.filter(
            member_id=self.kwargs['pk'],
            date__gte=self.request.POST['date_from'] + ' 00:00:00',
            date__lte=self.request.POST['date_to'] + ' 23:59:59',
            payment_type=self.request.POST['payment_type'],
        ).order_by('-date')

        total_payments = queryset.aggregate(Sum('amount'))

        total_contributions = Payment.objects.filter(
            member_id=self.kwargs['pk'],
            date__gte=self.request.POST['date_from'] + ' 00:00:00',
            date__lte=self.request.POST['date_to'] + ' 23:59:59',
            payment_type=self.request.POST['payment_type'],
            payment_type__flag='contribution'
        ).aggregate(Sum('amount'))

        total_loans_repaid = Payment.objects.filter(
            member_id=self.kwargs['pk'],
            date__gte=self.request.POST['date_from'] + ' 00:00:00',
            date__lte=self.request.POST['date_to'] + ' 23:59:59',
            payment_type=self.request.POST['payment_type'],
            payment_type__flag='loan_repayment',
        ).aggregate(Sum('amount'))

        context = {
            'statement': queryset,
            'filters_form': AllPaymentsFiltersForm,
            'member': member,
            'total_payments': total_payments,
            'total_contributions': total_contributions,
            'total_loans_repaid': total_loans_repaid,
        }

        return render(request, self.template_name, context=context)


class ListAllPayments(PermissionRequiredMixin, ListView, FormView):
    model = Payment
    template_name = 'payments/list-payments.html'
    paginate_by = 20
    now = datetime.now()
    permission_required = "payments.change_payment"
    raise_exception = True
    permission_denied_message = 'You dont have permission to view peoples contributions'

    def get(self, request, *args, **kwargs):

        # query all payments starting this year January
        queryset = Payment.objects.filter(payment_type__flag='saving_account').order_by('-date')

        paginator = Paginator(queryset, self.paginate_by)

        page = request.GET.get('page', 1)

        try:
            contributions = paginator.page(page)
        except PageNotAnInteger:
            contributions = paginator.page(1)
        except EmptyPage:
            contributions = paginator.page(paginator.num_pages)

        total_payments = queryset.aggregate(Sum('amount'))

        total_contributions = Payment.objects.filter(
            date__gte=str(self.now.year) + '-01-01 00:00:00',
            payment_type__flag='saving_account'
        ).aggregate(Sum('amount'))

        total_loans_repaid = Payment.objects.filter(
            date__gte=str(self.now.year) + '-01-01 00:00:00',
            payment_type__flag='loan_repayment'
        ).aggregate(Sum('amount'))

        context = {
            'contributions': contributions,
            'total_payments': total_payments,
            'total_contributions': total_contributions,
            'total_loans_repaid': total_loans_repaid,
            'filters_form': AllPaymentsFiltersForm
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        if not self.request.POST['payment_type'] or not self.request.POST['date_from'] or not self.request.POST['date_to']:
            messages.error(request, 'Error, required value(s) missing', extra_tags='alert alert-danger')
            return render(request, self.template_name, {'filters_form': AllPaymentsFiltersForm})

        queryset = Payment.objects.filter(
            date__gte=self.request.POST['date_from'] + ' 00:00:00',
            date__lte=self.request.POST['date_to'] + ' 23:59:59',
            payment_type=self.request.POST['payment_type']
        )

        total_payments = queryset.aggregate(Sum('amount'))

        total_contributions = Payment.objects.filter(
            date__gte=self.request.POST['date_from'] + ' 00:00:00',
            date__lte=self.request.POST['date_to'] + ' 23:59:59',
            payment_type=self.request.POST['payment_type'],
            payment_type__flag='saving_account'
        ).aggregate(Sum('amount'))

        total_loans_repaid = Payment.objects.filter(
            date__gte=self.request.POST['date_from'] + ' 00:00:00',
            date__lte=self.request.POST['date_to'] + ' 23:59:59',
            payment_type=self.request.POST['payment_type'],
            payment_type__flag='loan_repayment'
        ).aggregate(Sum('amount'))

        context = {
            'filters_form': AllPaymentsFiltersForm,
            'contributions': queryset,
            'total_payments': total_payments,
            'total_contributions': total_contributions,
            'total_loans_repaid': total_loans_repaid,
            'date_from': self.request.POST['date_from'],
            'date_to': self.request.POST['date_to'],
        }

        return render(request, self.template_name, context=context)


class UpdatePaymentType(PermissionRequiredMixin, UpdateView):
    model = PaymentType
    template_name = 'payments/update-type.html'
    form_class = UpdatePaymentTypeForm
    permission_denied_message = 'You dont have permission to edit page'
    raise_exception = True
    permission_required = 'paymenttype.change_paymenttype'

    def post(self, request, *args, **kwargs):

        instance = self.model.objects.get(
            pk=self.kwargs['pk']
        )
        slug = instance.payment_type.replace(' ', '_').lower()

        form = UpdatePaymentTypeForm(data=request.POST, instance=instance)

        if form.is_valid():

            payment_type = form.save(commit=False)

            new_slug = form.cleaned_data['payment_type'].replace(' ', '_').lower()

            payment_type.slug = new_slug
            payment_type.save()

            # Update built-in accounting account
            account, created = BuiltInAccount.objects.get_or_create(
                slug=slug
            )

            messages.success(request, 'Success, account updated', extra_tags='alert alert-success')

            account.slug = new_slug
            account.account_name = form.cleaned_data['payment_type']

            account.save()

            return redirect(to='payments:list-types')
        else:
            messages.error(request, 'Errors occured', extra_tags='alert alert-danger')

            return render(request, self.template_name, {'form': form})


class DeletePaymentType(PermissionRequiredMixin, DeleteView):
    model = PaymentType
    permission_required = 'paymenttype.change_paymenttype'
    success_url = '/payments/list-types/'

    def get_success_url(self):

        messages.success(self.request, 'Success, payment account has been deleted', extra_tags='alert alert-info')

        return self.success_url


class ListPaymentTypes(LoginRequiredMixin, ListView):
    model = PaymentType
    template_name = 'payments/list-types.html'
    paginate_by = 20


class MakePaymentType(PermissionRequiredMixin, CreateView):
    model = PaymentType
    template_name = 'payments/create_type.html'
    form_class = PaymentTypeForm
    permission_required = 'Add payment type'

    def post(self, request, *args, **kwargs):

        form = PaymentTypeForm(data=request.POST)

        if form.is_valid():

            payment_type = form.save(commit=False)
            slug = form.cleaned_data['payment_type'].replace(' ', '_').lower()

            payment_type.slug = slug
            payment_type.save()

            # Create built-in accounting account
            account = BuiltInAccount(
                slug=slug,
                account_name=form.cleaned_data['payment_type'],
            )
            account.save()

            messages.success(request, 'Payment type was created', extra_tags='alert alert-success')

            return redirect(to='payments:list-types')
        else:

            context = {
                'form': form
            }
            messages.error(request, 'Errors occured', extra_tags='alert alert-danger')

            return render(request, self.template_name, context=context)








