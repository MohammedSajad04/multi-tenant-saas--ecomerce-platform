from django.urls import path
from .views import ( TenantRegisterView, PendingTenantListView,ApproveTenantView )
from .views import ( SuperAdminCompaniesView, ApproveCompanyView )
from .views import ( CompanyDetailView, RejectCompanyView ,BlockCompanyView ,UnblockCompanyView, 
                    CompanySubscriptionView)
from .views import (
    CreatePaymentView,
    VerifyPaymentView
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
    path(
    'superadmin/companies/',
    SuperAdminCompaniesView.as_view()
    ),
    path(
        'superadmin/approve/<int:tenant_id>/',
        ApproveCompanyView.as_view()
    ),
    path(
        "superadmin/company/<int:tenant_id>/",
        CompanyDetailView.as_view()
    ),
    path(
        "superadmin/reject/<int:tenant_id>/",
        RejectCompanyView.as_view()
    ),
    path(
        "superadmin/block/<int:tenant_id>/",
        BlockCompanyView.as_view()
    ),
    path(
        "superadmin/unblock/<int:tenant_id>/",
        UnblockCompanyView.as_view()
    ),
    path(
        'subscription/',
        CompanySubscriptionView.as_view()
    ),
    path(
        "create-payment/",
        CreatePaymentView.as_view()
    ),
    path(
        "verify-payment/",
        VerifyPaymentView.as_view()
    ),
]
