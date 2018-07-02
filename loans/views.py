from django.shortcuts import (render, redirect, get_object_or_404, get_list_or_404)
from django.views.generic import (CreateView, ListView, DetailView, FormView)
from django.views.generic.edit import (UpdateView, DeleteView,)
from .models import (Loan, LoanRequest, Disbursement, LoanRepayment,)
from payments.models import (Payment,)
from members.models import Member
from notifications.models import Notification
from .forms import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import (PermissionDenied,)
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,)
from django.conf import settings
from django.core.exceptions import (ObjectDoesNotExist,)
import json, arrow, calendar
from django.core.mail import send_mail
from easy_pdf.views import PDFTemplateView
from reports.models import TrialBalance
from .amort import LoanArmotizer, get_emi
from website.models import (FooterCenter, FooterLeft, FooterRight)
from django.db.models import Sum
import pytz

now = datetime.now(tz=pytz.timezone('Africa/Nairobi'))


class ViewDisbursedLoan(LoginRequiredMixin, DetailView):
    template_name = 'loans/view_disbursed_loan.html'
    model = LoanRequest

    def get(self, request, *args, **kwargs):

        loan_request = get_object_or_404(LoanRequest, pk=self.kwargs['pk'])

        try:

            disbursement = get_object_or_404(Disbursement, loan_request_id=loan_request.pk)
        except ObjectDoesNotExist:

            disbursement = None

        days_in_current_month = calendar.monthrange(now.year, now.month)[1]

        if disbursement:

            first_due_date = disbursement.first_due - timedelta(days=days_in_current_month)
            loan_amount = disbursement.amount_disbursed
            interest = disbursement.interest_rate
            payment = disbursement.get_emi()
            term = disbursement.repayment_period
        else:
            first_due_date = datetime.today()
            loan_amount = 200000
            interest = 12
            term = 24
            payment = get_emi(term=term, loan_type='reducing_balance', rate=interest, principal=loan_amount)

        loan = LoanArmotizer(
            originDate=first_due_date,
            loanAmount=loan_amount,
            interest=interest,
            payment=payment,
            dueDay=first_due_date.day,
            days="actual",
            basis="actual",
            numberOfPayments=term,
            period="monthly")

        schedule = loan.amort()

        epochs = []

        dates = {}

        for d in schedule:  # build dates dictionary
            dates[int(d['num'])] = d['date']

        date_today = datetime.strptime(now.strftime("%Y-%m-%d"), "%Y-%m-%d")

        for item in schedule:

            if item['num'] == 1:  # is first payment, use date disbursed
                payment_date_from = disbursement.date_disbursed

                payment_date_from = payment_date_from.strftime("%Y-%m-%d")

                payment_date_to = dates.get(item['num'])
            else:
                payment_date_from = dates.get(item['num']-1, disbursement.date_disbursed)

                payment_date_to = dates.get(item['num'])

            epoch_repayments = LoanRepayment.objects.filter(
                loan_request_id=loan_request.pk,
                payment_date__gt=payment_date_from,
                payment_date__lte=payment_date_to
            ).aggregate(
                Sum('credit')
            )

            item_date = datetime.strptime(item['date'], "%Y-%m-%d")
            item_date = item_date.replace(tzinfo=pytz.timezone('Africa/Nairobi'))
            date_today = datetime.strptime(now.strftime("%Y-%m-%d"), "%Y-%m-%d")
            date_today = date_today.replace(tzinfo=pytz.timezone('Africa/Nairobi'))

            if item['num'] - 1 > 0:
                previous_epoch_date = dates.get(item['num'] - 1, disbursement.date_disbursed)
                previous_epoch_date = datetime.strptime(previous_epoch_date, "%Y-%m-%d")
                previous_epoch_date = previous_epoch_date.replace(tzinfo=pytz.timezone('Africa/Nairobi'))
            else:
                previous_epoch_date = disbursement.date_disbursed
                previous_epoch_date = previous_epoch_date.replace(tzinfo=pytz.timezone('Africa/Nairobi'))

            if item_date >= date_today and previous_epoch_date <= date_today:
                is_current = True
            else:
                is_current = False

            epoch = {
                'num': item['num'],
                'date': arrow.get(item['date'], "YYYY-M-D").strftime("%d-%m-%Y"),
                'emi': item['emi'],
                'is_current': is_current,
                'total_repayments': epoch_repayments,
                'date_from': payment_date_from,
                'date_to': payment_date_to,
                'date_today': date_today
            }

            epochs.append(epoch)

        context = {
            'loan_request': loan_request,
            'disbursement': disbursement,
            'schedule': schedule,
            'epochs': epochs,
            'current_epoch': date_today,
            'dates': dates,
        }
        return render(self.request, self.template_name, context=context)


class PrintLoanStatus(PDFTemplateView):
    template_name = 'loans/print-loan-status-pdf.html'

    def get_context_data(self, **kwargs):

        context = super(PrintLoanStatus, self).get_context_data(**kwargs)

        loan_request = get_object_or_404(LoanRequest, pk=self.kwargs['pk'])

        context['title'] = ' LOAN APPLICATION '

        context['loan_request'] = loan_request

        if loan_request.status == 'disbursed':
            disbursement = Disbursement.objects.get(loan_request_id=loan_request.pk)
            context['disbursement'] = disbursement

        # check if there are guarantors and pass them to template
        guarantors = Guarantor.objects.filter(loan_request_id=loan_request.pk)

        if guarantors.count() > 0:
            context['guarantors'] = guarantors

        return context


class PrintRepaymentStatement(PDFTemplateView):
    template_name = 'loans/print-loan-repayment-pdf.html'

    def get_context_data(self, **kwargs):

        context = super(PrintRepaymentStatement, self).get_context_data(**kwargs)

        loan_request = get_object_or_404(LoanRequest, pk=self.kwargs['pk'])

        context['title'] = loan_request.loan.name + ' statement : '

        date_from = '2000-01-01 00:00:00'
        date_to = '2100-12-31 23:59:59'

        if self.request.GET.get('date_from'):
            date_from = self.request.GET.get('date_from') + ' 00:00:00'

        if self.request.GET.get('date_to'):
            date_to = self.request.GET.get('date_to') + ' 23:59:59'

        context['loan_repayments'] = LoanRepayment.objects.filter(
            payment_date__gte=date_from,
            payment_date__lte=date_to,
            loan_request_id=loan_request.pk
        )
        context['date_from'] = date_from
        context['date_to'] = date_to

        return context


class ViewArmotizedSchedule(LoginRequiredMixin, FormView):
    template_name = 'loans/armotization_schedule.html'

    def post(self, request, *args, **kwargs):

        form = ArmotizedForm(data=request.POST)
        schedule = []
        total_repayable = 0

        if form.is_valid():

            loan_amount = form.cleaned_data['loan_amount']
            interest = form.cleaned_data['interest_rate']
            number_of_payments = form.cleaned_data['term']
            interest_on = form.cleaned_data['type']

            loan = LoanArmotizer(
                originDate=now.strftime("%Y-%m-%d"),
                loanAmount=loan_amount,
                interest=interest,
                payment=get_emi(loan_amount, interest, number_of_payments, interest_on),
                days="actual",
                basis="actual",
                numberOfPayments=number_of_payments,
                period="monthly")

            schedule = loan.amort()

            total_repayable = get_emi(loan_amount, interest, number_of_payments, interest_on) * number_of_payments

        context = {
            'form': form,
            'schedule': schedule,
            'total_repayable': total_repayable
        }
        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        context = {}

        if self.request.GET.get('loan_request_id'):
            disbursement = get_object_or_404(Disbursement, loan_request_id=self.request.GET.get('loan_request_id'))
            context['loan_request'] = disbursement.loan_request

            loan_amount = disbursement.amount_disbursed
            interest = disbursement.interest_rate
            interest_on = disbursement.interest_on
            number_of_payments = disbursement.repayment_period
            emi = get_emi(loan_amount, interest, number_of_payments, interest_on)
            origin_date = disbursement.first_due - timedelta(days=30)
        else:
            # Set default values
            loan_amount = 200000
            interest = 12
            number_of_payments = 24
            interest_on = 'reducing_balance'
            emi = get_emi(loan_amount, interest, number_of_payments, interest_on)
            origin_date = now.strftime("%Y-%m-%d")

        loan = LoanArmotizer(
            originDate=origin_date,
            loanAmount=loan_amount,
            interest=interest,
            payment=emi,
            days="actual",
            basis="actual",
            numberOfPayments=number_of_payments,
            period="monthly")

        schedule = loan.amort()

        form = ArmotizedForm(initial={
            'type': interest_on,
            'loan_amount': loan_amount,
            'term': number_of_payments,
            'interest_rate': interest,
        })

        context['form'] = form
        context['schedule'] = schedule
        context['total_repayable'] =  emi * number_of_payments

        return render(request, self.template_name, context=context)


class ViewArmotizedScheduleWebsite(FormView):
    template_name = 'loans/loan-calculator.html'

    def post(self, request, *args, **kwargs):

        form = ArmotizedForm(data=request.POST)

        if form.is_valid():

            loan_amount = form.cleaned_data['loan_amount']
            interest = form.cleaned_data['interest_rate']
            number_of_payments = form.cleaned_data['term']
            interest_on = form.cleaned_data['type']
            emi = get_emi(loan_amount, interest, number_of_payments, interest_on)

        else:
            """ Form is not valid, use these default values to generate a schedule. 
                Submitted form will still have submitted values
            """
            loan_amount = 200000
            interest = 12
            number_of_payments = 24
            interest_on = 'reducing_balance'
            emi = get_emi(loan_amount, interest, number_of_payments, interest_on)

        loan = LoanArmotizer(
            originDate=now.strftime("%Y-%m-%d"),
            loanAmount=loan_amount,
            interest=interest,
            payment=emi,
            days="actual",
            basis="actual",
            numberOfPayments=number_of_payments,
            period="monthly"
        )

        schedule = loan.amort()

        context = {
            'form': form,
            'schedule': schedule,
            'footer_left': FooterLeft.objects.first(),
            'footer_center': FooterCenter.objects.first(),
            'footer_right': FooterRight.objects.first(),
            'total_repayable': emi * number_of_payments
        }
        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        # Set default values
        loan_amount = 200000
        interest = 12
        number_of_payments = 24
        interest_on = 'reducing_balance'
        emi = get_emi(loan_amount, interest, number_of_payments, interest_on)

        if self.request.GET.get('loan_request_id'):
            disbursement = get_object_or_404(Disbursement, loan_request_id=self.request.GET.get('loan_request_id'))

            loan_amount = disbursement.amount_disbursed
            interest = disbursement.interest_rate
            interest_on = disbursement.interest_on
            number_of_payments = disbursement.repayment_period
            emi = get_emi(loan_amount, interest, number_of_payments, interest_on)

        loan = LoanArmotizer(
            originDate=now.strftime("%Y-%m-%d"),
            loanAmount=loan_amount,
            interest=interest,
            payment=emi,
            days="actual",
            basis="actual",
            numberOfPayments=number_of_payments,
            period="monthly"
        )

        schedule = loan.amort()

        form = ArmotizedForm(initial={
            'type': interest_on,
            'loan_amount': loan_amount,
            'term': number_of_payments,
            'interest_rate': interest,
        })

        context = {
            'form': form,
            'schedule': schedule,
            'footer_left': FooterLeft.objects.first(),
            'footer_center': FooterCenter.objects.first(),
            'footer_right': FooterRight.objects.first(),
            'total_repayable': emi * number_of_payments
        }
        return render(request, self.template_name, context=context)


class ApproveGuaranteeRequest(LoginRequiredMixin, FormView):
    # permission_required = 'loans:request_loan'
    template_name = 'loans/approve-guarantee-request.html'

    def post(self, request, *args, **kwargs):

        loan_request = LoanRequest.objects.get(pk=self.kwargs['pk'])

        guarantor_request = Guarantor.objects.get(
            guarantor_id=self.request.user.pk,
            loan_request_id=loan_request.pk
        )

        form = ApproveGuaranteeRequestForm(data=request.POST)

        context = {
            'loan_request': loan_request,
            'guarantor_request': guarantor_request,
        }

        if form.is_valid():

            guarantor_request.status = form.cleaned_data['choice']

            guarantor_request.response_message = form.cleaned_data['response_message']

            guarantor_request.save()

            messages.success(request, 'Response was made, thank you.', extra_tags='alert alert-info')

            # Generate notification

            member = self.request.user.get_full_name()

            if guarantor_request.status == 'rejected':
                not_message = 'Your request to ' + member + ' to guarantee loan was rejected'
                title = 'Guarantor request rejected'
            else:
                not_message = 'Your request to ' + member + ' was accepted'
                title = 'Guarantor request approved'

            notification = Notification(
                title=title,
                sender_id=self.request.user.pk,
                to=loan_request.requested_by,
                notification=not_message + '<p>' + guarantor_request.response_message + "</p>",
            )

            notification.save()

            # send email to creditor
            try:
                send_mail(
                    subject=title,
                    message='',
                    html_message=notification.notification,
                    from_email='wecanys2@gmail.com',
                    recipient_list=[notification.sender.email],
                    fail_silently=True,
                )
            except Exception as e:
                pass

        else:

            context['form'] = ApproveGuaranteeRequestForm

            messages.error(request, 'Errors ocurred', extra_tags='alert alert-danger')

        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        loan_request = LoanRequest.objects.get(pk=self.kwargs['pk'])

        try:
            guarantor_request = Guarantor.objects.get(
                guarantor_id=self.request.user.pk,
                loan_request_id=loan_request.pk
            )
            not_requested = None

        except ObjectDoesNotExist:
            guarantor_request = None,
            not_requested = "This member has not requested you to guarantee any loans."

        if loan_request.status not in ('approved', 'disbursed'):

            form = ApproveGuaranteeRequestForm
        else:
            form = None

        context = {
            'loan_request': loan_request,
            'form': form,
            'not_requested': not_requested,
            'guarantor_request': guarantor_request
        }
        return render(request, self.template_name, context=context)


class ListGuaranteeRequests(LoginRequiredMixin, ListView):
    model = Guarantor
    template_name = "loans/list-guarantee-requests.html"
    context_object_name = "requests_list"
    ordering = "-pk"

    def get_queryset(self):

        return self.model.objects.filter(
            guarantor=self.request.user
        )


class SearchGuarantor(LoginRequiredMixin, FormView):
    template_name = 'loans/search-guarantor.html'

    def get(self, request, *args, **kwargs):

        loan_request = LoanRequest.objects.get(pk=self.kwargs['pk'])

        if not self.request.user == loan_request.requested_by:
            raise PermissionDenied("You can not request guarantor on behalf of other member")

        context = {
            'loan_request': loan_request,
            'guarantor_form': RequestGuarantorForm
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        try:

            member = Member.objects.get(member_number=request.POST.get('member_number'))
            # loan_request = LoanRequest.objects.get(pk=self.kwargs['pk'])

            response = json.dumps({
                'name': member.get_full_name(),
                'pk': member.pk,
                'member_number': member.member_number,
                'success': 'true'
            })

        except ObjectDoesNotExist as exp:

            response = json.dumps({'err': str(exp), })

        return HttpResponse(response)


class RequestGuarantor(LoginRequiredMixin, FormView):

    def get(self, request, *args, **kwargs):

        return redirect(to='loans:search-guarantor', pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):

        loan_request = LoanRequest.objects.get(pk=self.kwargs['pk'])

        if not self.request.user == loan_request.requested_by:
            messages.error(request, 'You can not request guarantor on behalf of others !', extra_tags='alert alert-danger')
            return redirect(to='loans:search-guarantor', pk=self.kwargs['pk'])

        context = {
            'loan_request': loan_request,
            'guarantor_form': RequestGuarantorForm,
            'formd': request.POST,
        }

        guarantor_requested = get_object_or_404(Member, member_number=request.POST.get('member_number'))

        if self.request.user.pk == guarantor_requested.pk:
            messages.error(request, 'You can not guarantee yourself !', extra_tags='alert alert-danger')
            return redirect(to='loans:search-guarantor', pk=self.kwargs['pk'])

        guarantor_test = Guarantor.objects.filter(
            loan_request_id=self.kwargs['pk'],
            guarantor_id=guarantor_requested.pk
        ).count()

        context['guarantor_test'] = guarantor_test

        if guarantor_test > 0:
            messages.error(request, 'Guarantor request already sent', extra_tags='alert alert-info')
            return redirect(to='loans:search-guarantor', pk=self.kwargs['pk'])
        else:

            g_request = Guarantor(
                guarantor=guarantor_requested,
                loan_request_id=self.kwargs['pk'],
                amount=request.POST.get('amount'),
                status='pending',
                response_message='',
            )

            g_request.save()

            messages.error(request, 'Success, request sent', extra_tags='alert alert-success')

            # Send notifications

            title = "Request to guarantee loan"
            message = "%s requested you to guarantee their %s for an amount of %s" % (self.request.user.get_full_name(), loan_request.loan.name, request.POST.get('amount'))
            html_message = "<br><a href='http://wecanyouthsacco.co.ke/loans/list-guarantee-requests/'>Login</a> to approve request."

            send_mail(
                subject=title,
                message="",
                html_message=message + html_message,
                from_email="info@wecanyouthsacco.co.ke",
                recipient_list=[guarantor_requested.email, ],
                fail_silently=True
            )

            notification = Notification(
                title=title,
                notification=message + html_message,
                to_id=guarantor_requested.pk,
                sender_id=self.request.user.pk
            )

            notification.save()

            return redirect(to='loans:search-guarantor', pk=self.kwargs['pk'])

        # return render(request, 'loans/search-guarantor.html', context=context)


class ShowLoanStatus(PermissionRequiredMixin, DetailView):
    model = LoanRequest
    template_name = 'loans/loan-status.html'
    permission_required = ['loans.can_manage_loans', ]
    raise_exception = True
    permission_denied_message = 'You don\'t have permission.'

    def has_permission(self):

        requested_by = Member.objects.get(
            pk=self.kwargs['pk']
        )

        # Allow a member to view own loan status
        if requested_by == self.request.user:
            return True

        # Allow those with required_permission to view all loan status
        if self.request.user.has_perms(self.permission_required):
            return True

    def get(self, request, *args, **kwargs):

        requested_by = Member.objects.get(
            pk=self.kwargs['pk']
        )

        form = LoanRepaymentFiltersForm(requested_by=requested_by)

        loan_requests = LoanRequest.objects.filter(requested_by=requested_by)

        loan_repayments = LoanRepayment.objects.prefetch_related(
            'loan_request__loanrepayment_set'
        ).filter(
            loan_request__requested_by=requested_by
        ).order_by('payment_date')

        context = {
            'form': form,
            'guarantor_form': RequestGuarantorForm,
            'loan_requests': loan_requests,
            'loan_repayments': loan_repayments,
            'requested_by': requested_by
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        requested_by = Member.objects.get(
            pk=self.kwargs['pk']
        )

        if not (self.request.user.is_staff or self.request.user.is_superuser or (requested_by == self.request.user)):
            raise PermissionDenied

        try:
            loan_requests = LoanRequest.objects.filter(
                requested_by=requested_by
            )

            loan_repayments = LoanRepayment.objects.filter(
                loan_request__requested_by=requested_by
            )
        except ObjectDoesNotExist:
            loan_requests = None
            loan_repayments = None

        form = LoanRepaymentFiltersForm(
            data=request.POST,
            requested_by=requested_by
        )
        if form.is_valid():
            # overwrite repayment_statement to apply form filters
            try:
                loan_repayments = LoanRepayment.objects.filter(
                    loan_request__requested_by=requested_by,
                    loan_request_id=request.POST.get('loan_request', '')
                )
            except ObjectDoesNotExist:
                loan_repayments = None

        context = {
            'form': form,
            'loan_requests': loan_requests,
            'loan_repayments': loan_repayments,
            'requested_by': requested_by
        }

        return render(request, self.template_name, context=context)


class RepayLoan(PermissionRequiredMixin, CreateView):
    permission_required = 'loans.can_manage_loans'
    permission_denied_message = 'You don\'t have permission to manage loans'
    raise_exception = True
    model = LoanRepayment
    template_name = 'loans/repay_loan.html'

    def get(self, request, *args, **kwargs):

        loan_requests = LoanRequest.objects.filter(
            pk=self.kwargs['pk']
        )

        loan_request = loan_requests.get()

        disbursement = get_object_or_404(Disbursement, loan_request_id=loan_request.pk)

        member = Member.objects.get(pk=loan_request.requested_by_id)

        initial = {
            'loan_request': loan_request,
            'credit': round(disbursement.get_emi(), 2)
        }

        form = LoanRepaymentForm(initial=initial, emi=initial['credit'], loan_request=loan_requests)

        context = {
            'member': member,
            'form': form,
            'loan_request': loan_request,
            'emi': initial['credit']
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        loan_requests = LoanRequest.objects.filter(
            pk=self.kwargs['pk']
        )

        loan_request = loan_requests.get()

        member = Member.objects.get(pk=loan_request.requested_by_id)

        disbursement = Disbursement.objects.get(loan_request_id=loan_request.pk)

        initial = {
            'credit': round(disbursement.get_emi(), 2)
        }

        form = LoanRepaymentForm(emi=initial['credit'], data=request.POST, loan_request=loan_requests)

        if form.is_valid():

            loan_request = form.cleaned_data['loan_request']

            amount_outstanding = loan_request.get_amount_outstanding()

            credit = float(form.cleaned_data['credit'])

            new_repayment = LoanRepayment(
                credit=credit,
                loan_request_id=loan_request.pk,
                outstanding=amount_outstanding - credit,
                next_due=loan_request.next_due(),
                total_paid=credit + loan_request.get_total_repaid(),
                description='Repayment'
            )

            new_repayment.save()

            messages.success(request, 'Success, repayment was been made.', extra_tags='alert alert-success')

            return redirect(to='loans:loan-status', pk=member.pk)

        else:  # form is not valid

            messages.error(request, 'Invalid or missing form values ... try again.', extra_tags='alert alert-danger')

            return redirect(to='loans:repay-loan', member_id=member.pk)


class ListDisbursements(PermissionRequiredMixin, ListView):
    model = Disbursement
    template_name = 'loans/list-disbursements.html'
    context_object_name = 'disbursements'
    ordering = '-date_disbursed'
    permission_required = 'loans.view_loan_disbursements'
    raise_exception = True
    permission_denied_message = 'You dont have permission to access page'
    paginate_by = 10


class DisburseLoan(PermissionRequiredMixin, CreateView):
    model = Disbursement
    permission_required = 'loans.can_manage_loans'
    raise_exception = True
    permission_denied_message = "You don't have permission to disburse loans"
    template_name = 'loans/disburse-loan.html'

    def get(self, request, *args, **kwargs):

        loan_request = get_object_or_404(LoanRequest, id=self.kwargs['request_id'])

        form = DisbursementForm

        return render(request, self.template_name, {'loan_request': loan_request, 'form': form})

    def post(self, request, *args, **kwargs):

        loan_request = get_object_or_404(LoanRequest, id=self.kwargs['request_id'])

        form = DisbursementForm(
            data=request.POST
        )

        if form.is_valid():

            """TODO: Introduce transaction"""

            disbursed = form.save(commit=False)
            disbursed.loan_request_id = self.kwargs['request_id']
            disbursed.next_due = form.cleaned_data['first_due']
            disbursed.save()

            """Change loan request status to disbursed"""

            LoanRequest.objects.filter(
                id=self.kwargs['request_id']
            ).update(
                status='disbursed'
            )

            # updated loan instance
            loan_request = get_object_or_404(
                LoanRequest,
                id=self.kwargs['request_id']
            )

            """Then create record for next_due date for first interest calculation"""
            Disbursement.objects.filter(
                loan_request_id=loan_request.id
            ).update(
                first_due=request.POST.get('first_due')
            )

            disbursement = get_object_or_404(
                Disbursement,
                loan_request_id=loan_request.id
            )

            # Add first record in loan repayment statement
            repayment = LoanRepayment(
                debit=form.cleaned_data['amount_disbursed'],
                description='Amount disbursed',
                loan_request_id=loan_request.pk,
                next_due=request.POST.get('first_due'),
                total_paid=0.0,
                outstanding=disbursement.get_emi() * disbursement.repayment_period
            )
            repayment.save()

            # Update trial balance

            trial_balance = TrialBalance(
                module='Loans',
                debit=form.cleaned_data['amount_disbursed'],
                credit=0.0,
                member_id=loan_request.requested_by.pk,
                staff=self.request.user.get_full_name(),
                description=loan_request.loan.name
            )

            trial_balance.save()

            messages.success(request, 'Success, amount disbursed.', extra_tags='alert alert-success')

            context = {
                'loan': loan_request,
                'settings': settings,
                'loan_request': loan_request,
                'is_disbursed': True,
            }
            return redirect(to='loans:view-disbursed-loan', pk=loan_request.pk)

        else:  # form not valid

            messages.error(request, 'Error, amount not disbursed', extra_tags='alert alert-danger')

            return render(request, self.template_name, {'form': form, 'loan': loan_request})


class ApproveLoan(PermissionRequiredMixin, UpdateView):
    model = LoanRequest
    template_name = 'loans/approve-loan.html'
    context_object_name = 'loan'
    form_class = LoanApprovalForm
    permission_denied_message = 'You do not have permission to manage loans'
    raise_exception = True
    permission_required = 'loans.can_manage_loans'

    def post(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=self.kwargs['pk'])
        form = self.form_class(data=request.POST, instance=instance)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, loan status has been updated', extra_tags='alert alert-success')
            return render(request, self.template_name, {'form': form, 'loan': instance})
        else:
            messages.error(request, 'Error, loan not approved', extra_tags='alert alert-danger')
            return render(request, self.template_name, {'form': form, 'loan': instance})


class ListApplications(PermissionRequiredMixin, ListView):
    model = LoanRequest
    context_object_name = 'applications'
    template_name = 'loans/list-applications.html'
    paginate_by = 10
    ordering = '-date_requested'
    permission_required = 'loans.view_requests'
    raise_exception = True


class ApplyLoan(LoginRequiredMixin, CreateView):
    model = LoanRequest
    loans = Loan.objects.all()
    template_name = 'loans/apply-loan.html'

    def get(self, request, *args, **kwargs):

        form = LoanApplicationForm
        return render(request, self.template_name, {'loans': self.loans, 'form': form})

    def post(self, request, *args, **kwargs):

        form = LoanApplicationForm(data=request.POST)

        if form.is_valid():

            loan_request = form.save(commit=False)
            loan_request.requested_by = self.request.user

            loan_request.save()
            messages.success(request, 'Success, loan request submitted', extra_tags='alert alert-success')

            return redirect(to='loans:search-guarantor', pk=loan_request.pk)
        else:
            messages.error(request, 'Error, loan request failed.', extra_tags='alert alert-success')
            return render(request, self.template_name, {'form': form})


class DeleteLoan(PermissionRequiredMixin, DeleteView):
    model = Loan
    success_url = '/loans/list'
    permission_required = 'loans.delete_loan'
    permission_denied_message = 'You dont have permission to delete loan products'
    raise_exception = True


class UpdateLoan(PermissionRequiredMixin, UpdateView):
    model = Loan
    template_name = 'loans/update.html'
    context_object_name = 'loan'
    form_class = UpdateLoanForm
    permission_required = 'loans.can_change_loan'
    raise_exception = True
    permission_denied_message = 'You dont have permission to change loan products'

    def post(self, request, *args, **kwargs):

        if not self.request.user.is_superuser:
            raise PermissionDenied

        instance = self.model.objects.get(pk=self.kwargs['pk'])
        form = self.form_class(data=request.POST, instance=instance)

        if form.is_valid():
            form.save()
            messages.success(request, 'Success, loan details updated', extra_tags='alert alert-success')
            return redirect(to='/loans/list')
        else:
            messages.error(request, 'Error: Failed updating loan details', extra_tags='alert alert-danger')
            return render(request, self.template_name, {'form': form})


class ListLoans(LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'loans/list.html'
    context_object_name = 'loans'
    paginate_by = 10


class CreateLoanType(PermissionRequiredMixin, CreateView):
    model = Loan
    template_name = 'loans/create-loan.html'
    permission_required = ('loans.add_loan',)
    raise_exception = True
    permission_denied_message = 'You dont have permission to create loan products'
    form_class = CreateLoanForm

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, Loan type created', extra_tags='alert alert-success')

            return redirect(to='/loans/list')
        else:
            messages.error(request, 'Error: Failed creating loan type', extra_tags='alert alert-danger')

            return render(request, self.template_name, {'form': form})
