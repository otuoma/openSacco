from django.shortcuts import render, redirect, get_object_or_404
from fines.models import Fine
from members.models import Member
from fines.forms import CreateFineForm, PayFineForm, UpdateFineForm
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,)
from django.contrib import messages
from fines.utils import Amount_outstanding
from members.models import Member
from django.db.models import Sum


class PayFine(PermissionRequiredMixin, CreateView):
    model = Fine
    template_name = 'fines/pay-fine.html'
    permission_required = ['fines.add_fine']
    raise_exception = True
    permission_denied_message = 'You dont have permission to manage fines.'

    def post(self, request, *args, **kwargs):

        members = Member.objects.filter(pk=self.kwargs['pk'])

        if members.count() == 0:
            raise Member.DoesNotExist

        member = members.get()

        fines = Fine.objects.filter(member_account_id=self.kwargs['pk'])

        amount_outstanding = Amount_outstanding(fines)

        form = PayFineForm(member_account=members, data=request.POST)

        if form.is_valid():

            fine = form.save(commit=False)

            if amount_outstanding > 0 :

                fine.amount_outstanding = amount_outstanding - form.cleaned_data['credit']
            else:
                fine.amount_outstanding = amount_outstanding - form.cleaned_data['credit']

            fine.created_by_id = self.request.user.pk

            fine.save()

            messages.success(request, 'Success, fine was paid', extra_tags='alert alert-success')

            return redirect(to='fines:list-member-fines', pk=self.kwargs['pk'])
        else:

            messages.error(request, 'Failed, errors occured in the form', extra_tags='alert alert-danger')

        context = {
            'member': member,
            'amount_outstanding': amount_outstanding,
            'form': form
        }

        return render(request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):

        members = Member.objects.filter(pk=self.kwargs['pk'])

        if members.count() == 0:
            raise Member.DoesNotExist()

        member = members.get()

        fines = Fine.objects.filter(member_account_id=self.kwargs['pk'])

        amount_outstanding = Amount_outstanding(fines)

        initial = {'member_account': member}

        form = PayFineForm(member_account=members, initial=initial)

        context = {
            'amount_outstanding': amount_outstanding,
            'member': member,
            'form': form,
        }
        return render(request, self.template_name, context=context)


class ListMemberFines(PermissionRequiredMixin, ListView):
    model = Fine
    template_name = "fines/list-member-fines.html"
    context_object_name = 'fines'
    permission_denied_message = "Sorry you dont have permission to access page"
    permission_required = ['fines.change_fine', ]
    raise_exception = True

    def has_permission(self):

        member = get_object_or_404(Member, pk=self.kwargs['pk'])

        if member.has_perms(self.permission_required) or self.request.user.pk == self.kwargs['pk']:

            return True

    def get(self, request, *args, **kwargs):

        member = get_object_or_404(Member, pk=self.kwargs['pk'])

        fines = Fine.objects.filter(member_account_id=self.kwargs['pk'])

        amount_outstanding = Amount_outstanding(fines)

        context = {
            'member': member,
            'fines': fines,
            'amount_outstanding': amount_outstanding
        }
        return render(request, self.template_name, context=context)


class ListFines(PermissionRequiredMixin, ListView):
    model = Fine
    template_name = 'fines/list-fines.html'
    raise_exception = True
    permission_required = ['fines.add_fine', ]
    permission_denied_message = 'Sorry, you don\'t have permission to view members fines'

    def get(self, request, *args, **kwargs):

        fines = Fine.objects.all()

        members = fines.values_list('member_account_id', flat=True).distinct()

        members = Member.objects.filter(pk__in=members)

        obj = []

        total_credit = fines.aggregate(Sum('credit'))
        total_debit = fines.aggregate(Sum('debit'))

        if total_credit['credit__sum'] is None:
            total_credit['credit__sum'] = 0.0

        if total_debit['debit__sum'] is None:
            total_debit['debit__sum'] = 0.0

        amount_outstanding = total_debit['debit__sum'] - total_credit['credit__sum']

        for member in members:

            items = dict()

            items['member'] = member

            items['fines'] = fines.filter(member_account_id=member.pk)

            items['amount_outstanding'] = Amount_outstanding(items['fines'])

            obj.append(items)

        context = {
            'fines': obj,
            'total_credit': total_credit,
            'total_debit': total_debit,
            'amount_outstanding': amount_outstanding
        }

        return render(request, self.template_name, context=context)


class CreateFine(PermissionRequiredMixin, CreateView):
    model = Fine
    permission_required = ['fines.add_fine', ]
    template_name = 'fines/create-fine.html'
    raise_exception = True
    permission_denied_message = "You don't have permission to add fines"
    form_class = CreateFineForm

    def get(self, request, *args, **kwargs):

        members = Member.objects.filter(pk=self.kwargs['pk'])

        member = members.get()

        fines = Fine.objects.filter(member_account_id=self.kwargs['pk'])

        amount_outstanding = Amount_outstanding(fines)

        initial = {
            'member_account': member,
        }

        context = {
            'form': self.form_class(
                member_account=members,
                initial=initial,
            ),
            'member': member,
            'amount_outstanding': amount_outstanding
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        members = Member.objects.filter(pk=self.kwargs['pk'])

        member = members.get()

        form = self.form_class(member_account=members, data=request.POST)

        if form.is_valid():

            fine = form.save(commit=False)

            fines = Fine.objects.filter(member_account_id=self.kwargs['pk'])

            fine.created_by_id = self.request.user.pk

            fine.amount_outstanding = Amount_outstanding(fines) + form.cleaned_data['debit']

            fine.save()

            messages.success(request, 'Success, fine was added.', extra_tags='alert alert-success')

            return redirect(to="fines:list-member-fines", pk=self.kwargs['pk'])
        else:

            context = {
                'form': form,
                'member': member
            }

            messages.error(request, 'Failed, errors occurred in the form.', extra_tags='alert alert-danger')

            return render(request, self.template_name, context=context)


class UpdateFine(PermissionRequiredMixin, UpdateView):
    model = Fine
    permission_required = 'fines.change_fine'
    raise_exception = True
    form_class = UpdateFineForm
    template_name = 'fines/update-fine.html'

    def get(self, request, *args, **kwargs):

        fine = get_object_or_404(Fine, pk=self.kwargs['pk'])

        member = Member.objects.filter(pk=fine.member_account_id)

        fines = Fine.objects.filter(member_account_id=fine.member_account_id)

        amount_outstanding = Amount_outstanding(fines)

        initial = {
            'member_account': member.get(),
            'debit': fine.debit,
            'description': fine.description
        }

        context = {
            'fine': fine,
            'member': member.get(),
            'amount_outstanding': amount_outstanding,
            'form': self.form_class(
                member_account=member,
                initial=initial,
            ),
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        fine = get_object_or_404(Fine, pk=self.kwargs['pk'])

        member = Member.objects.filter(pk=fine.member_account_id)

        fines = Fine.objects.filter(member_account_id=fine.member_account_id)

        amount_outstanding = Amount_outstanding(fines)

        form = self.form_class(member_account=member, data=request.POST, instance=fine)

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, fine has been updated', extra_tags='alert alert-success')

            return redirect(to='fines:list-member-fines', pk=member.get().pk)

        else:

            context = {
                'fine': fine,
                'member': member.get(),
                'amount_outstanding': amount_outstanding,
                'form': form,
            }

            messages.error(request, 'Error, fine not updated', extra_tags='alert alert-danger')

            return render(request, self.template_name, context=context)

















