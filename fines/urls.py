from django.urls import path
from . import views


app_name = 'fines'

urlpatterns = [

    path('create-fine/<int:pk>', views.CreateFine.as_view(), name='create-fine'),
    path('pay-fine/<int:pk>', views.PayFine.as_view(), name='pay-fine'),
    path('list-fines/', views.ListFines.as_view(), name='list-fines'),
    path('update-fine/<int:pk>', views.UpdateFine.as_view(), name='update-fine'),
    path('list-member-fines/<int:pk>', views.ListMemberFines.as_view(), name='list-member-fines'),
]

