from django.urls import path
from .views import (

    TenantRegisterView,
    PendingTenantListView,
    ApproveTenantView
)
urlpatterns = [
    path(
        'register/',
        TenantRegisterView.as_view()
    ),
    path(
        'pending/',
        PendingTenantListView.as_view()
    ),
    path(
        'approve/<int:tenant_id>/',
        ApproveTenantView.as_view()
    ),
]