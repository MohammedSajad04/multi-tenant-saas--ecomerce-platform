from django.urls import path

from .views import (
    CompanyCustomersView,
    CompanyDashboardView,
    CompanyOrdersView,
    CompanyProductsView,
    CreateOrderView,
    ProductCreateView,
    ProductDetailView,
    ProductListView,
    MyOrdersView,
    UpdateOrderStatusView,
    CreateOrderPaymentView,
    VerifyOrderPaymentView,
)


urlpatterns = [

    path(

        'create/',

        ProductCreateView.as_view()
    ),


    path(

        'list/',

        ProductListView.as_view()
    ),

    path(

        'company-products/',

        CompanyProductsView.as_view()
    ),

    path(

        'detail/<int:product_id>/',

        ProductDetailView.as_view()
    ),

    path(

        'order/<int:product_id>/',

        CreateOrderView.as_view()
    ),
    path(

        'dashboard/',

        CompanyDashboardView.as_view()
    ),
    path(

        'company-orders/',

        CompanyOrdersView.as_view()
    ),

    path(

        'customers/',

        CompanyCustomersView.as_view()
    ),
    path(
        'my-orders/',
        MyOrdersView.as_view()
    ),

    path(
        'update-order/<int:order_id>/',
        UpdateOrderStatusView.as_view()
    ),

    path(
        "create-payment/",
        CreateOrderPaymentView.as_view()
    ),

    path(
        "verify-payment/",
        VerifyOrderPaymentView.as_view()
    ),
]
