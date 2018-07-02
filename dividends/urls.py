from django.urls import path
from . import views


app_name = 'dividends'

urlpatterns = [

    path('list-disbursements/', views.ListDisbursements.as_view(), name='list-disbursements'),
    path('create-issue/', views.CreateDividendIssue.as_view(), name='create-issue'),
    path('list-issues/', views.ListDividendIssues.as_view(), name='list-issues'),
    path('calculate-dividends/', views.CalculateDividends.as_view(), name='calculate-dividends'),
    path('update/<int:pk>', views.UpdateDividendIssue.as_view(), name='update-issue'),
    path('delete-issue/<int:pk>', views.DeleteDividendsIssue.as_view(), name='delete-issue'),
    path('member-disbursements/<int:member_id>', views.ListMemberDisbursements.as_view(), name='member-disbursements'),
]

