from django.shortcuts import render, redirect
from shares.models import Share, MemberShare
from shares.forms import SetupSharesForm, AddSharesForm
from members.models import Member
from reports.models import TrialBalance
from django.contrib import messages
from django.views.generic import FormView, ListView, TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin,)
from django.db.models import Sum
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)


class ShareDistribution(LoginRequiredMixin, ListView):
    model = MemberShare
    template_name = 'shares/share-distribution.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):

        shares = MemberShare.objects.all().order_by('-pk')

        paginator = Paginator(shares, self.paginate_by)

        page = request.GET.get('page', 1)

        share = Share.objects.first()

        if share is None:
            share_value = 0
            aggregate = None
        else:
            share_value = share.share_value
            aggregate = shares.aggregate(Sum('quantity'))

        try:
            shares_list = paginator.page(page)
        except PageNotAnInteger:
            shares_list = paginator.page(1)
        except EmptyPage:
            shares_list = paginator.page(paginator.num_pages)

        context = {
            'shares_list': shares_list,
            'share_value': share_value,
            'total_bought': aggregate
        }

        return render(request, self.template_name, context=context)


class AddShares(PermissionRequiredMixin, FormView):
    # model = MemberShare
    template_name = 'shares/add-shares.html'
    permission_required = 'shares.can_create_shares'
    raise_exception = True
    permission_denied_message = 'You dont have permission to add shares'

    def get(self, request, *args, **kwargs):

        context = {}

        context['member'] = Member.objects.get(pk=self.kwargs['pk'])
        context['form'] = AddSharesForm(member=Member.objects.filter(pk=self.kwargs['pk']))

        share = Share.objects.first()

        if share is None:
            messages.error(request, 'Can not add shares, share value is not setup.', extra_tags='alert alert-danger')
            return redirect(to='shares:shares-home')

        try:
            context['member_shares'] = MemberShare.objects.get(
                member=context['member']
            )

            context['share_value'] = share.share_value * context['member_shares'].quantity

        except ObjectDoesNotExist:

            context['member_shares'] = None

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        form_qty = int(request.POST.get('quantity'))

        # if form_qty == 0:
        #
        #     messages.error(request, 'Error, can not assign 0 shares', extra_tags='alert alert-danger')
        #
        #     return redirect(to='members:profile', pk=self.kwargs['pk'])

        share = Share.objects.first()

        if share is None:
            messages.error(request, 'Can not add shares, share module is not setup.', extra_tags='alert alert-danger')
            return redirect(to='shares:shares-home')

        share_obj, created_share = MemberShare.objects.update_or_create(
            member_id=self.kwargs['pk']
        )

        old_qty = share_obj.quantity

        share_obj.quantity = form_qty

        share_obj.save()

        messages.success(request, 'Success, shares updated', extra_tags='alert alert-success')

        return redirect(to='members:profile', pk=self.kwargs['pk'])


class SharesHome(LoginRequiredMixin, FormView):
    template_name = 'shares/shares-home.html'

    def get(self, request, *args, **kwargs):

        share = Share.objects.first()

        if share is None:
            share_value = 0
        else:
            share_value = share.share_value

        context = {
            'total_bought': MemberShare.objects.all().aggregate(Sum('quantity')),
            'form': SetupSharesForm,
            'share_value': share_value
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        share = Share.objects.first()

        form = SetupSharesForm(
            data=request.POST,
            instance=share
        )

        if form.is_valid():

            form.save()

            messages.success(request, 'Success, share values updated ', extra_tags='alert alert-success')

        else:  # form not valid

            messages.error(request, 'Failed ...', extra_tags='alert alert-danger')

        return redirect(to='shares:shares-home')
