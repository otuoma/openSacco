from django.urls import path
from pettycash import views


app_name = 'pettycash'

urlpatterns = [
    path('list-expenditures/', views.ListExpenditures.as_view(), name='list-expenditures'),
    path('add-expenditure/', views.AddExpenditure.as_view(), name='add-expenditure'),
    path('update-expenditure/<int:pk>/', views.UpdateExpenditure.as_view(), name='update-expenditure'),
]