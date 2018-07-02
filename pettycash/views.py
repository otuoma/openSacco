from django.shortcuts import render, redirect
from django.views.generic import (CreateView, FormView, UpdateView)
from pettycash.models import Expenditure
from pettycash.forms import (AddExpenditureForm, FilterExpendituresForm, UpdateExpenditureForm)
from django.contrib import messages
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,)
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from reports.models import TrialBalance


class UpdateExpenditure(PermissionRequiredMixin, UpdateView):
    model = Expenditure
    template_name = 'pettycash/update-expenditure.html'
    permission_required = 'Change Expenditure'
    form_class = UpdateExpenditureForm

    def post(self, request, *args, **kwargs):

        instance = self.model.objects.get(pk=self.kwargs['pk'])
        form = self.form_class(request.POST, instance=instance)

        if form.is_valid():

            form.save()

            trial_balance = TrialBalance.objects.get(pk=instance.pk)

            trial_balance.module = 'Petty cash'
            trial_balance.debit = form.cleaned_data['amount']
            trial_balance.credit = form.cleaned_data['credit']
            trial_balance.member_id = self.request.user.pk
            trial_balance.staff = self.request.user.get_full_name()
            trial_balance.description = form.cleaned_data['description']

            trial_balance.save()

            messages.success(request, 'Success, expenditure updated', extra_tags='alert alert-success')

            return redirect(to='pettycash:list-expenditures')
        else:
            messages.error(request, 'Errors occurred', extra_tags='alert alert-danger')

            context = {
                'form': form
            }
            return render(request, self.template_name, context=context)


class ListExpenditures(LoginRequiredMixin, FormView):
    model = Expenditure
    template_name = 'pettycash/list-expenditures.html'

    def post(self, request, *args, **kwargs):

        form = FilterExpendituresForm(data=request.POST)

        if form.is_valid():
            expenditure_list = self.model.objects.filter(
                date__gte=request.POST.get('date_from', ''),
                date__lte=request.POST.get('date_to', '')
            ).order_by('-date')
        else:
            expenditure_list = self.model.objects.all().order_by('-date')

        total = expenditure_list.aggregate(Sum('amount'))

        context = {
            'expenditures': expenditure_list,
            'form': form,
            'total': total
        }
        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):
        expenditures = self.model.objects.all().order_by('-date')

        total = expenditures.aggregate(Sum('amount'))

        form = FilterExpendituresForm(data=None)

        paginator = Paginator(expenditures, per_page=20)

        page = request.GET.get('page', 1)

        try:
            expenditure_list = paginator.page(page)
        except PageNotAnInteger:
            expenditure_list = paginator.page(1)
        except EmptyPage:
            expenditure_list = paginator.page(paginator.num_pages)

        context = {
            'expenditures': expenditure_list,
            'form': form,
            'total': total
        }
        return render(request, self.template_name, context=context)


class AddExpenditure(LoginRequiredMixin, CreateView):
    model = Expenditure
    template_name = 'pettycash/add-expenditure.html'

    def get(self, request, *args, **kwargs):

        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied

        context = {
            'form': AddExpenditureForm
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied

        form = AddExpenditureForm(data=request.POST)

        if form.is_valid():

            expenditure = form.save(commit=False)

            expenditure.member = self.request.user

            expenditure.save()

            trial_balance = TrialBalance(
                module='Petty cash',
                debit=form.cleaned_data['amount'],
                credit=0.0,
                member_id=self.request.user.pk,
                staff=self.request.user.get_full_name(),
                description=form.cleaned_data['description']
            )

            trial_balance.save()

            messages.success(request, 'Success, expenditure created', extra_tags='alert alert-success')

            return redirect(to='pettycash:list-expenditures')
        else:
            messages.success(request, 'Error, expenditure not created.', extra_tags='alert alert-danger')

        context = {
            'form': form
        }
        return render(request, self.template_name, context=context)








