"""wecan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls,),
    path('', home_view.LoadHome.as_view(), name='home'),
    path('send-contact-message', home_view.SendContactMessage.as_view(), name='send-contact-message'),
    path('fines/', include('fines.urls'), name='fines'),
    path('accounting/', include('accounting.urls', namespace='accounting'), name='accounting'),
    path('downloads/', home_view.ViewDownloads.as_view(), name='downloads'),
    path('faqs/', home_view.ViewFAQS.as_view(), name='faqs'),
    path('members/', include('members.urls', namespace='members'), name='members'),
    path('payments/', include('payments.urls', namespace='payments'), name='payments'),
    path('loans/', include('loans.urls', namespace='loans'), name='loans'),
    path('pettycash/', include('pettycash.urls', namespace='pettycash'), name='pettycash'),
    path('dividends/', include('dividends.urls', namespace='dividends'), name='dividends'),
    path('notifications/', include('notifications.urls', namespace='notifications'), name='notifications'),
    path('shares/', include('shares.urls', namespace='shares'), name='shares-home'),
    path('reports/', include('reports.urls', namespace='reports'), name='reports')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
