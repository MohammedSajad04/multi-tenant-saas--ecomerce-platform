from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Tenant


from .serializers import (

    TenantRegisterSerializer,
    TenantSerializer
)
from accounts.models import User

class TenantRegisterView(APIView):
    def post(self, request):
        serializer = TenantRegisterSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Company registration request submitted successfully"
                },

                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PendingTenantListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tenants = Tenant.objects.filter(
            status='pending'
        )
        serializer = TenantSerializer(
            tenants,
            many=True
        )
        return Response(serializer.data)


class ApproveTenantView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(
                id=tenant_id
            )
        except Tenant.DoesNotExist:
            return Response(
                {
                    "error": "Tenant not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        tenant.status = "approved"
        tenant.save()
        username = tenant.company_name.lower().replace(" ", "_")
        password = "123456"
        company_admin = User.objects.create_user(
            username=username,
            email=tenant.company_email,
            password=password,
            role='company_admin',
            tenant=tenant
        )
        return Response(
            {
                "message": "Tenant approved successfully",
                "company_admin_username": username,
                "password": password
            },
            status=status.HTTP_200_OK
        )