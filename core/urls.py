from django.urls import path
from .views import AIChatView, ChatHistoryView

urlpatterns = [

    path(
        "chat/",
        AIChatView.as_view()
    ),

    path(
        "history/<int:tenant_id>/",
        ChatHistoryView.as_view()
    ),
]