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

from django.urls import path
from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('', views.ChartOfAccounts.as_view(), name='chart-of-accounts'),
    path('update-account/<int:pk>', views.UpdateAccount.as_view(), name='update-account'),
    path('account-transactions/<int:pk>', views.ViewAccountTransactions.as_view(), name='account-transactions'),
    path('record-transaction/<int:pk>', views.RecordAccountTransaction.as_view(), name='record-transaction'),
    path('update-transaction/<int:pk>', views.UpdateAccountTransaction.as_view(), name='update-transaction'),
    path('delete-transaction/<int:pk>', views.DeleteTransaction.as_view(), name='delete-transaction'),
    path('delete-account/<int:pk>', views.DeleteAccount.as_view(), name='delete-account'),
    path('create-account/', views.CreateAccount.as_view(), name='create-account'),
    path('update-account-group/<int:pk>', views.UpdateAccountGroup.as_view(), name='update-account-group'),
    path('delete-account-group/<int:pk>', views.DeleteAccountGroup.as_view(), name='delete-account-group'),
    path('create-account-group/', views.CreateAccountGroup.as_view(), name='create-account-group'),
    path('trial-balance/', views.TrialBalance.as_view(), name='trial-balance'),
]




