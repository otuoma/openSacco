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
from loans import views

app_name = 'loans'

urlpatterns = [
    path('', views.ListLoans.as_view(), name='loans'),
    path('view-disbursed-loan/<int:pk>/', views.ViewDisbursedLoan.as_view(), name='view-disbursed-loan'),
    path('armotization-schedule-website/', views.ViewArmotizedScheduleWebsite.as_view(), name='armotization-schedule-website'),
    path('armotization-schedule/', views.ViewArmotizedSchedule.as_view(), name='armotization-schedule'),
    path('disburse-loan/<int:request_id>/', views.DisburseLoan.as_view(), name='disburse-loan'),
    path('approve-loan/<int:pk>/', views.ApproveLoan.as_view(), name='approve-loan'),
    path('list-applications/', views.ListApplications.as_view(), name='list-applications'),
    path('list-disbursements/', views.ListDisbursements.as_view(), name='list-disbursements'),
    path('apply-loan/', views.ApplyLoan.as_view(), name='apply-loan'),
    path('delete/<int:pk>/', views.DeleteLoan.as_view(), name='delete'),
    path('update/<int:pk>/', views.UpdateLoan.as_view(), name='update'),
    path('list', views.ListLoans.as_view(), name='list-loans'),
    path('create-loan/', views.CreateLoanType.as_view(), name='create-loan'),
    path('loan-status/<int:pk>/', views.ShowLoanStatus.as_view(), name='loan-status'),
    path('print-repayment-statement/<int:pk>/', views.PrintRepaymentStatement.as_view(), name='print-repayment-statement'),
    path('print-loan-status/<int:pk>/', views.PrintLoanStatus.as_view(), name='print-loan-status'),
    path('repay-loan/<int:pk>/', views.RepayLoan.as_view(), name='repay-loan'),
    path('request-guarantor/<int:pk>', views.RequestGuarantor.as_view(), name='request-guarantor'),
    path('search-guarantor/<int:pk>', views.SearchGuarantor.as_view(), name='search-guarantor', ),
    path('approve-guarantee-request/<int:pk>', views.ApproveGuaranteeRequest.as_view(), name='approve-guarantee-request', ),
    path('list-guarantee-requests/', views.ListGuaranteeRequests.as_view(), name='list-guarantee-requests', ),
]

