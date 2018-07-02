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
from members import views

app_name = 'members'

urlpatterns = [
    path('welcome', views.Welcome.as_view(), name='welcome'),
    path('create-member', views.CreateMember.as_view(), name='create-member'),
    path('admin-create-member', views.AdminCreateMember.as_view(), name='admin-create-member'),
    path('bulk-upload-members', views.BulkMemberUpload.as_view(), name='bulk-upload-members'),
    path('directory', views.MemberDirectory.as_view(), name='directory'),
    path('login', views.Login.as_view(), name='login',),
    path('logout', views.Logout.as_view(), name='logout',),
    path('profile/<int:pk>/', views.MemberProfile.as_view(), name='profile', ),
    path('request-password-reset/', views.RequestPasswordReset.as_view(), name='request-password-reset'),
    path('reset-requested-password/', views.ResetRequestedPassword.as_view(), name='reset-requested-password'),
    path('set-permissions/<int:pk>/', views.SetPermissions.as_view(), name='set-permissions', ),
    path('edit-bank-account/<int:account_id>/', views.EditBankAccount.as_view(), name='edit-bank-account', ),
    path('create-bank-account/<int:member_id>/', views.CreateBankAccount.as_view(), name='create-bank-account', ),
    path('edit-member/<int:pk>/', views.EditMember.as_view(), name='edit-member', ),
    path('activate-account/<int:pk>/', views.ActivateAccount.as_view(), name='activate-account', ),
    path('create-password/<int:pk>/', views.CreatePassword.as_view(), name='create-password', ),
    path('change-password/', views.ChangePassword.as_view(), name='change-password', ),
    path('deactivate-account/<int:pk>/', views.DeactivateAccount.as_view(), name='deactivate-account', ),
    path('upload-profile-photo/<int:pk>/', views.UploadProfilePhoto.as_view(), name='upload-profile-photo', ),
    path('print-members-list', views.PrintMembersList.as_view(), name='print-members-list'),
    path('filter-members-list', views.FilterMembersList.as_view(), name='filter-members-list'),
    path('upload-scanned-id/<int:pk>', views.UploadScannedID.as_view(), name='upload-scanned-id'),
    path('', views.MemberDirectory.as_view(), ),
]
