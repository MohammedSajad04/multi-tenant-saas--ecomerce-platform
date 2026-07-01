from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Tenant
from accounts.models import User
from datetime import date
from datetime import timedelta
from .serializers import SubscriptionSerializer
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import SubscriptionPayment
from .serializers import TenantDropdownSerializer
from .serializers import ( TenantRegisterSerializer,TenantSerializer )
from products.models import Order


class TenantRegisterView(APIView):
    def post(self, request):
        serializer = TenantRegisterSerializer(
            data=request.data
        )
        if serializer.is_valid():
            try:
                serializer.save()

            except Exception as e:

                return Response(
                    {
                        "error": str(e)
                    },
                    status=400
                )
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
            status='pending',
            is_deleted = False
        )
        serializer = TenantSerializer(
            tenants,
            many=True
        )
        return Response(serializer.data)

class CompanyDropdownView(APIView):

    def get(self, request):

        companies = Tenant.objects.filter(
        status="approved",
        is_deleted=False
    )

        serializer = TenantDropdownSerializer(
            companies,
            many=True
        )

        return Response(
            serializer.data
        )


class ApproveCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, tenant_id):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            tenant = Tenant.objects.get(id=tenant_id)

        except Tenant.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        tenant.status = "approved"
        tenant.subscription_plan = "trial"
        tenant.save()


        send_mail(
            subject="Company Approved",
            message=f"""
        Hello {tenant.owner_name},

        Congratulations!

        Your company has been approved.

        You can now log in using the email and password you created during registration.

        Login Email:
        {tenant.company_email}

        Regards,
        SaaS Platform Team
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[tenant.company_email],
            fail_silently=True
        )

        return Response(
            {
                "message": "Company approved successfully"
            },
            status=status.HTTP_200_OK
        )
            

class SuperAdminCompaniesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        companies = Tenant.objects.filter(
            is_deleted=False
        ).order_by("-created_at")

        serializer = TenantSerializer(
            companies,
            many=True
        )

        return Response(serializer.data)

class CompanyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tenant_id):
        # Check if user is superuser
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Fetch the company with the new conditions
        company = Tenant.objects.filter(
            id=tenant_id,
            is_deleted=False
        ).first()

        # Handle case where company is not found or doesn't meet conditions
        if not company:
            return Response(
                {"error": "Company not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize and return the data
        serializer = TenantSerializer(company)
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
            tenant = Tenant.objects.get(id=tenant_id)

        except Tenant.DoesNotExist:

            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        reason = request.data.get(
            "reason",
            "No reason provided."
        )

        tenant.status = "rejected"
        tenant.rejection_reason = reason
        tenant.save()

        send_mail(
            subject="Company Registration Rejected",
            message=f"""
        Hello {tenant.owner_name},

        Unfortunately your company registration has been rejected.

        Reason:

        {reason}

        If you believe this is a mistake you may contact support.

        Regards,
        SaaS Platform Team
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[tenant.company_email],
            fail_silently=True,
        )

        return Response({
            "message": "Company rejected successfully"
        })
    
class BlockCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, tenant_id):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            tenant = Tenant.objects.get(id=tenant_id)

        except Tenant.DoesNotExist:

            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        reason = request.data.get(
            "reason",
            "No reason provided."
        )

        tenant.status = "blocked"
        tenant.blocked_reason = reason
        tenant.rejection_reason = ""
        tenant.save()

        User.objects.filter(
            tenant=tenant
        ).update(
            is_blocked=True
        )

        send_mail(
            subject="Company Blocked",
            message=f"""
        Hello {tenant.owner_name},

        Your company has been blocked.

        Reason:

        {reason}

        Please contact support.

        Regards,
        SaaS Platform Team
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[tenant.company_email],
            fail_silently=True,
        )

        return Response({
            "message": "Company blocked successfully"
        })

class UnblockCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, tenant_id):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            tenant = Tenant.objects.get(id=tenant_id)

        except Tenant.DoesNotExist:

            return Response(
                {"error": "Company not found"},
                status=404
            )

        tenant.status = "approved"
        tenant.blocked_reason = ""
        tenant.rejection_reason = ""
        tenant.save()

        User.objects.filter(
            tenant=tenant
        ).update(
            is_blocked=False
        )

        send_mail(
            subject="Company Unblocked",
            message=f"""
        Hello {tenant.owner_name},

        Your company has been unblocked.

        You may now access the platform again.

        Regards,
        SaaS Platform Team
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[tenant.company_email],
            fail_silently=True,
        )

        return Response({
            "message": "Company unblocked successfully"
        })
    
class DeleteCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, tenant_id):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            tenant = Tenant.objects.get(id=tenant_id)

        except Tenant.DoesNotExist:

            return Response(
                {"error": "Company not found"},
                status=404
            )

        reason = request.data.get(
            "reason",
            "No reason provided."
        )

        tenant.deleted_reason = reason
        tenant.is_deleted = True
        tenant.deleted_at = timezone.now()
        tenant.save()

        User.objects.filter(
            tenant=tenant
        ).update(
            is_blocked=True
        )

        send_mail(
            subject="Company Deleted",
            message=f"""
        Hello {tenant.owner_name},

        Your company account has been deleted.

        Reason:

        {reason}

        Regards,
        SaaS Platform Team
        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[tenant.company_email],
            fail_silently=True,
        )

        return Response({
            "message": "Company deleted successfully"
        })

    
class CompanySubscriptionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        tenant=request.user.tenant

        if not tenant:

            return Response(
                {"error":"No company assigned"},
                status=400
            )

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
        if not tenant:
            return Response(
                {
                    "error":"No company assigned"
                },
                status=400
            )
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

        if not tenant:
            return Response(
                {
                    "error":"Tenant not found"
                },
                status=404
            )

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
    

class PlatformSubscriptionsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        subscriptions = SubscriptionPayment.objects.filter(
            tenant__is_deleted=False
        ).select_related(
            "tenant"
        ).order_by("-created_at")

        data = []

        for sub in subscriptions:

            data.append({

                "id": sub.id,

                "company_id": sub.tenant.id,

                "company": sub.tenant.company_name,

                "plan": sub.plan,

                "amount": sub.amount,

                "payment_status": sub.status,

                "subscription_start":
                sub.tenant.subscription_start,

                "subscription_end":
                sub.tenant.subscription_end,

                "subscription_status":
                (
                    "Active"
                    if sub.tenant.subscription_end
                    else "Expired"
                )
            })

        return Response(data)

# tenants/views.py
from collections import defaultdict
from calendar import month_abbr


class PlatformAnalyticsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        payments = SubscriptionPayment.objects.filter(
            status="paid"
        )

        total_revenue = sum(
            payment.amount
            for payment in payments
        )

        active_subscriptions = payments.count()

        total_orders = Order.objects.count()

        monthly_data = defaultdict(
            lambda: {
                "revenue": 0,
                "subscriptions": 0,
                "orders": 0
            }
        )

        for payment in payments:

            month = month_abbr[
                payment.created_at.month
            ]

            monthly_data[month]["revenue"] += float(
                payment.amount
            )

            monthly_data[month]["subscriptions"] += 1

        for order in Order.objects.all():

            month = month_abbr[
                order.created_at.month
            ]

            monthly_data[month]["orders"] += 1

        chart_data = []

        for month, values in monthly_data.items():

            chart_data.append({

                "month": month,

                "revenue":
                values["revenue"],

                "subscriptions":
                values["subscriptions"],

                "orders":
                values["orders"],
            })

        return Response({

            "total_users":
            User.objects.count(),

            "total_companies":
            Tenant.objects.filter(
                is_deleted=False
            ).count(),

            "active_subscriptions":
            active_subscriptions,

            "total_orders":
            total_orders,

            "total_revenue":
            total_revenue,

            "chart_data":
            chart_data,
        })

class SuperAdminDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        total_revenue = SubscriptionPayment.objects.filter(
            status="paid"
        )

        revenue = sum(
            payment.amount
            for payment in total_revenue
        )

        return Response({

            "tenant_count":
            Tenant.objects.filter(
                is_deleted=False
            ).count(),

            "user_count":
            User.objects.filter(
                is_blocked=False
            ).count(),

            "order_count":
            Order.objects.count(),

            "subscription_revenue":
            revenue,
        })
    
class CompanySubscriptionHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        payments = SubscriptionPayment.objects.filter(
            tenant_id=company_id
        ).order_by("-created_at")

        data = []

        for payment in payments:

            data.append({

                "id": payment.id,

                "plan": payment.plan,

                "amount": payment.amount,

                "status": payment.status,

                "payment_date": payment.created_at,
            })

        return Response(data)
    
