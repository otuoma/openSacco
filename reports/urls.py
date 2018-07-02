from django.urls import path
from reports import views


app_name = 'reports'

urlpatterns = [
    path('show-trial-balance/', views.ShowTrialBalance.as_view(), name='show-trial-balance'),
]