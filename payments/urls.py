from django.urls import path
from payments import views


app_name = 'payments'

urlpatterns = [
    path('statement/<int:pk>', views.Statement.as_view(), name='statement'),
    path('make-payment-type/', views.MakePaymentType.as_view(), name='make-payment-type'),
    path('upload-contributions/', views.UploadContributions.as_view(), name='upload-contributions'),
    path('list-payments/', views.ListAllPayments.as_view(), name='list-payments'),
    path('make-payment/<int:pk>/', views.MakePayment.as_view(), name='make-payment'),
    path('update-payment/<int:pk>/', views.UpdatePayment.as_view(), name='update-payment'),
    path('list-types/', views.ListPaymentTypes.as_view(), name='list-types'),
    path('update-type/<int:pk>/', views.UpdatePaymentType.as_view(), name='update-type'),
    path('delete-type/<int:pk>/', views.DeletePaymentType.as_view(), name='delete-type'),
    path('print-contributions/', views.PrintContributions.as_view(), name='print-contributions'),
    path('print-statememt/<int:pk>', views.PrintStatement.as_view(), name='print-statement'),
    path('', views.ListPaymentTypes.as_view(), ),
]