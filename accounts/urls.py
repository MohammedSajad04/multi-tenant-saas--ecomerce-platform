from django.urls import path
from .views import CurrentUserView
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView)
from .views import ( SuperAdminUsersView, ChangeUserRoleView)

urlpatterns = [
    path('me/', CurrentUserView.as_view()),
    path('login/',TokenObtainPairView.as_view()),
    path('refresh/',TokenRefreshView.as_view()),
    path('superadmin/users/', SuperAdminUsersView.as_view()),
    path('superadmin/change-role/<int:user_id>/',ChangeUserRoleView.as_view()),
]
