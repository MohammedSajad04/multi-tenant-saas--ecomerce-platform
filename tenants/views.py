from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Tenant
from .serializers import TenantSerializer
from accounts.models import User
from tenants.tasks import send_company_approval_email
from datetime import date
from datetime import timedelta
from .serializers import SubscriptionSerializer
import razorpay
from django.conf import settings
from .models import SubscriptionPayment

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

class SuperAdminCompaniesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Unauthorized"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(
            tenants,
            many=True
        )
        return Response(serializer.data)


class ApproveCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, tenant_id):

        if not request.user.is_superuser:

            return Response(
                {
                    "error": "Unauthorized"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:

            tenant = Tenant.objects.get(
                id=tenant_id
            )

        except Tenant.DoesNotExist:

            return Response(
                {
                    "error": "Company not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        tenant.status = "approved"

        # No trial activation here
        tenant.subscription_plan = None

        tenant.subscription_start = None

        tenant.subscription_end = None

        tenant.auto_renew = False

        tenant.is_trial_used = False

        tenant.save()

        username = (
            tenant.company_name
            .lower()
            .replace(" ", "_")
        )

        password = "123456"

        if not User.objects.filter(
            email=tenant.company_email
        ).exists():

            User.objects.create_user(
                username=username,
                email=tenant.company_email,
                password=password,
                role="company_admin",
                tenant=tenant
            )

        send_company_approval_email.delay(
            tenant.company_name,
            tenant.company_email,
            username,
            password
        )

        return Response(
            {
                "message":
                "Company approved successfully"
            }
        )
    

class CompanyDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, tenant_id):
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            tenant = Tenant.objects.get(
                id=tenant_id
            )
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)
    
class RejectCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, tenant_id):
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            tenant = Tenant.objects.get(
                id=tenant_id
            )
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        tenant.status = "rejected"
        tenant.save()
        return Response(
            {"message": "Company rejected"}
        )
    
class BlockCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, tenant_id):
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            tenant = Tenant.objects.get(
                id=tenant_id
            )
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        tenant.status = "blocked"
        tenant.save()
        return Response(
            {"message": "Company blocked"}
        )
    
class UnblockCompanyView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, tenant_id):
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            tenant = Tenant.objects.get(
                id=tenant_id
            )
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        tenant.status = "approved"
        tenant.save()
        return Response(
            {"message": "Company unblocked"}
        )
    
class CompanySubscriptionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        tenant = request.user.tenant

        serializer = SubscriptionSerializer(
            tenant
        )

        return Response(
            {
                "subscription":
                    serializer.data,

                "has_active_plan":
                    (
                        tenant.subscription_end
                        and
                        tenant.subscription_end >= date.today()
                    )
            }
        )

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        tenant = request.user.tenant
        plan = request.data.get(
            "plan"
        )
        prices = {
            "monthly": 499,
            "six_month": 2499,
            "yearly": 4999,
        }
        if plan not in prices:
            return Response(
                {
                    "error": "Invalid Plan"
                },
                status=400
            )
        amount = prices[plan]
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )
        razorpay_order = client.order.create(
            {
                "amount": amount * 100,
                "currency": "INR",
                "payment_capture": 1,
            }
        )
        payment = SubscriptionPayment.objects.create(
            tenant=tenant,
            plan=plan,
            amount=amount,
            razorpay_order_id=(
                razorpay_order["id"]
            )
        )
        return Response(
            {
                "payment_id": payment.id,
                "order_id": razorpay_order["id"],
                "amount": amount * 100,
                "key": settings.RAZORPAY_KEY_ID,
            }
        )

class VerifyPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        payment_id = request.data.get(
            "payment_id"
        )

        razorpay_payment_id = request.data.get(
            "razorpay_payment_id"
        )

        razorpay_order_id = request.data.get(
            "razorpay_order_id"
        )

        razorpay_signature = request.data.get(
            "razorpay_signature"
        )

        try:

            payment = SubscriptionPayment.objects.get(
                id=payment_id
            )

        except SubscriptionPayment.DoesNotExist:

            return Response(
                {
                    "error": "Payment record not found"
                },
                status=404
            )

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id":
                    razorpay_order_id,

                    "razorpay_payment_id":
                    razorpay_payment_id,

                    "razorpay_signature":
                    razorpay_signature,
                }
            )

        except Exception:

            payment.status = "failed"
            payment.save()

            return Response(
                {
                    "error": "Payment Failed"
                },
                status=400
            )

        payment.status = "paid"

        payment.razorpay_payment_id = (
            razorpay_payment_id
        )

        payment.save()

        tenant = payment.tenant

        tenant.subscription_plan = (
            payment.plan
        )

        tenant.subscription_start = (
            date.today()
        )

        tenant.auto_renew = True

        if payment.plan == "monthly":

            tenant.subscription_end = (
                date.today() +
                timedelta(days=30)
            )

        elif payment.plan == "six_month":

            tenant.subscription_end = (
                date.today() +
                timedelta(days=180)
            )

        elif payment.plan == "yearly":

            tenant.subscription_end = (
                date.today() +
                timedelta(days=365)
            )

        tenant.save()

        return Response(
            {
                "message":
                "Payment Successful"
            }
        )
    
class StartTrialView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        tenant = request.user.tenant

        if not tenant:

            return Response(
                {
                    "error": "No company assigned"
                },
                status=400
            )

        if tenant.is_trial_used:

            return Response(
                {
                    "error": "Free trial already used"
                },
                status=400
            )

        tenant.subscription_plan = "trial"

        tenant.subscription_start = date.today()

        tenant.subscription_end = (
            date.today() +
            timedelta(days=30)
        )

        tenant.is_trial_used = True

        tenant.save()

        return Response(
            {
                "message": "Trial Activated Successfully"
            }
        )