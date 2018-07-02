from django.shortcuts import render
from members.models import Member
from reports.models import TrialBalance
from reports.forms import FilterTrialBalanceForm
from django.views.generic import FormView, ListView


class ShowTrialBalance(ListView, FormView):
    model = TrialBalance
    context_object_name = 'trial_balance'
    template_name = 'reports/show-trial-balance.html'
    paginate_by = 10
    ordering = '-timestamp'
    form_class = FilterTrialBalanceForm

    def post(self, request, *args, **kwargs):

        form = FilterTrialBalanceForm(data=request.POST)

        if form.is_valid():

            date_from = request.POST.get('date_from') + ' 00:00:00'
            date_to = request.POST.get('date_to') + ' 23:59:59'

            trial_balance = self.model.objects.filter(
                timestamp__gte=date_from,
                timestamp__lte=date_to,
            ).order_by('-timestamp')
        else:
            trial_balance = self.model.objects.all().order_by('-timestamp')

        context = {
            'trial_balance': trial_balance,
            'form': form,
        }
        return render(request, self.template_name, context=context)



