from django.urls import path
from rest_framework_simplejwt.views import ( TokenRefreshView )
from .views import ( CompanySummaryView, CompanyUsersByCompanyView, CompanyUsersView, CurrentUserView, SuperAdminUsersView, ChangeUserRoleView, LoginView, UnblockUserView )
from .views import RegisterView
from .views import BlockUserView

urlpatterns = [

    path(
        'me/',
        CurrentUserView.as_view()
    ),

    path(
        'login/',
        LoginView.as_view()
    ),
    
    path(
    "register/",
    RegisterView.as_view()
    ),
    
    path(
        'refresh/',
        TokenRefreshView.as_view()
    ),

    path(
        'superadmin/users/',
        SuperAdminUsersView.as_view()
    ),

    path(
        'superadmin/change-role/<int:user_id>/',
        ChangeUserRoleView.as_view()
    ),
    path(
        "block-user/<int:user_id>/",
        BlockUserView.as_view()
    ),
    path(
        "superadmin/company-users/",
        CompanyUsersView.as_view()
    ),
    path(
        "superadmin/company-summary/",
        CompanySummaryView.as_view()
    ),
    path(
        "superadmin/company-users/<int:company_id>/",
        CompanyUsersByCompanyView.as_view()
    ),
    path(
        "unblock-user/<int:user_id>/",
         UnblockUserView.as_view()
),
]