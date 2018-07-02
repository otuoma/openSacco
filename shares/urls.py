"""wecan.shares URL Configuration

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
from shares import views

app_name = 'shares'

urlpatterns = [
    path('', views.SharesHome.as_view(), name='shares-home'),
    path('add-shares/<int:pk>/', views.AddShares.as_view(), name='add-shares'),
    path('share-distribution/', views.ShareDistribution.as_view(), name='share-distribution')
]
