from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView
)

from .views import (
    CurrentUserView,
    SuperAdminUsersView,
    ChangeUserRoleView,
    LoginView
)

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

]