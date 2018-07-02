from django.shortcuts import render
from notifications.models import Notification
from django.views.generic import (DetailView, ListView)
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from django.contrib.auth.mixins import (LoginRequiredMixin,)


class ViewNotifications(ListView):
    model = Notification
    template_name = 'notifications/list-notifications.html'
    context_object_name = 'notifications'
    paginate_by = 5

    def get(self, request, *args, **kwargs):

        notifications = Notification.objects.filter(to=self.request.user.pk).order_by('-date')

        paginator = Paginator(notifications, self.paginate_by)

        page = request.GET.get('page', 1)

        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            notifications = paginator.page(1)
        except EmptyPage:
            notifications = paginator.page(paginator.num_pages)

        context = {
            'notifications': notifications
        }

        return render(request, self.template_name, context=context)


class ViewNotification(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'notifications/read-notification.html'

    def get(self, request, *args, **kwargs):

        context = {
            'notification': Notification.objects.get(
                pk=self.kwargs['pk']
            )
        }

        if context['notification'].read is False:

            context['notification'].read = True
            context['notification'].save()

        return render(request, self.template_name, context=context)
