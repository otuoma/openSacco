from django.shortcuts import (render, redirect,)
from .models import (DividendIssue, DividendDisbursement, )
from payments.models import (Payment,)
from members.models import (Member,)
from .forms import (CreateDividendIssueForm, UpdateDividendIssueForm)
from django.views.generic.edit import (CreateView, DeleteView, UpdateView)
from django.views.generic import (ListView)
from django.contrib import messages
from django.contrib.auth import (PermissionDenied)
from datetime import datetime
from reports.models import TrialBalance


class ListMemberDisbursements(ListView):
    model = DividendDisbursement
    template_name = 'dividends/list_member_disbursements.html'

    def get(self, request, *args, **kwargs):
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        disbursements = DividendDisbursement.objects.filter(
            member_id=self.kwargs['member_id']
        )
        context = {
            'disbursements': disbursements
        }
        return render(request, self.template_name, context)


class ListDisbursements(ListView):
    model = DividendDisbursement
    template_name = 'dividends/list_disbursements.html'

    def get(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff ):
            raise PermissionDenied

        disbursements = DividendDisbursement.objects.all()
        context = {
            'disbursements': disbursements
        }
        return render(request, self.template_name, context)


class CalculateDividends(CreateView):
    model = DividendDisbursement
    template_name = 'dividends/calculate_dividends.html'

    def get(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        current_issue = DividendIssue.objects.order_by('id').filter().last()

        return render(request, self.template_name, context={'current_issue': current_issue})

    def post(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        current_issue = DividendIssue.objects.all().order_by('id').last()

        # Check if issue is already disbursed
        exists = DividendDisbursement.objects.filter(
            dividend_issue=current_issue
        )

        if exists.count() >= 1:
            messages.error(request, 'Error, this issue is already disbursed', extra_tags='alert alert-danger')
            return redirect(to='dividends:calculate-dividends')

        context = {'current_issue': current_issue}

        members = Member.objects.filter(is_active=True)

        if members.count() < 1:
            messages.error(request, 'Alert, no members were found on the database.', extra_tags='alert alert-info')
        else:
            errors, count = 0, 0

            for member in members:
                try:
                    amount = Payment.objects.filter(
                        member_id=member.id,
                        date__lte=datetime.strftime(current_issue.date_effective, '%Y-%m-%d 23:59:59')
                    ).order_by('date').last()

                    if amount is None:
                        continue

                    disbursement = DividendDisbursement.objects.create(
                        member_id=member.id,
                        dividend_issue=current_issue,
                        amount=(current_issue.percentage / 100) * amount.total
                    )
                    disbursement.save()

                    trial_balance = TrialBalance(
                        credit=0.0,
                        debit=disbursement.amount,
                        module='Dividends',
                        member=member,
                        staff=self.request.user.get_full_name(),
                        description=disbursement.dividend_issue.issue_name
                    )

                    trial_balance.save()

                    count += 1
                except Exception:
                    errors += 1
            if errors > 0:
                messages.error(request, str(errors)+' errors occured', extra_tags='alert alert-danger')
            else:
                messages.success(request, str(count)+' instances calculated.', extra_tags='alert alert-success')

            context['members'] = members

        return render(request, self.template_name, context)


class UpdateDividendIssue(UpdateView):
    model = DividendIssue
    template_name = 'dividends/update_issue.html'
    form_class = UpdateDividendIssueForm

    def get(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        issue = DividendIssue.objects.get(pk=self.kwargs['pk'])

        context = {
            'form': self.form_class(instance=issue),
            'dividendsissue': issue
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        issue = DividendIssue.objects.get(pk=self.kwargs['pk'])

        form = self.form_class(data=request.POST, instance=issue)

        context = {
            'form': form,
            'dividendsissue': issue
        }

        if form.is_valid():
            form.save()
            messages.success(request, 'Success, Issue updated', 'alert alert-success')
        else:
            messages.success(request, 'Error, update failed', 'alert alert-danger')

        return render(request, self.template_name, context=context)


class ListDividendIssues(ListView):
    model = DividendIssue
    template_name = 'dividends/list_issues.html'
    context_object_name = 'dividend_issues'
    ordering = '-pk'


class DeleteDividendsIssue(DeleteView):
    model = DividendIssue
    success_url = '/dividends/list-issues'


class CreateDividendIssue(CreateView):
    model = DividendIssue
    form_class = CreateDividendIssueForm
    template_name = 'dividends/create_issue.html'

    def get(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        return render(request, self.template_name, context={
            'form': self.form_class
        })

    def post(self, request, *args, **kwargs):

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            raise PermissionDenied

        form = CreateDividendIssueForm(data=self.request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Success, dividends issue created.', extra_tags='alert alert-success')
        else:
            messages.error(request, 'Error, dividends NOT created.', extra_tags='alert alert-danger')

        return redirect(to='dividends:list-issues')