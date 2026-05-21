from django.urls import path

from .views import (

    CompanyDashboardView,
    CreateOrderView,
    ProductCreateView,
    ProductDetailView,
    ProductListView
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
]
