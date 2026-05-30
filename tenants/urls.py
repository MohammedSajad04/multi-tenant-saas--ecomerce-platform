from django.urls import path
from .views import ( TenantRegisterView, PendingTenantListView,ApproveTenantView )
from .views import ( SuperAdminCompaniesView, ApproveCompanyView )

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
    path(

    'superadmin/companies/',

    SuperAdminCompaniesView.as_view()
    ),

    path(

        'superadmin/approve/<int:tenant_id>/',

        ApproveCompanyView.as_view()
    ),
]