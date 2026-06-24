from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.tasks import send_login_email
from django.contrib.auth.hashers import make_password
from tenants.models import Tenant
from django.contrib.auth.hashers import make_password



class RegisterView(APIView):

    def post(self, request):

        username = request.data.get("username")
        email = request.data.get("email")
        phone = request.data.get("phone")
        password = request.data.get("password")
        tenant_id = request.data.get("tenant")

        if User.objects.filter(email=email).exists():

            return Response(
                {
                    "error": "Email already exists"
                },
                status=400
            )

        if User.objects.filter(username=username).exists():

            return Response(
                {
                    "error": "Username already exists"
                },
                status=400
            )

        tenant = None

        if tenant_id:

            try:

                tenant = Tenant.objects.get(
                    id=tenant_id
                )

            except Tenant.DoesNotExist:

                return Response(
                    {
                        "error": "Company not found"
                    },
                    status=400
                )

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role="customer",
            tenant=tenant
        )

        return Response(
            {
                "message": "Registration Successful"
            }
        )
    


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class SuperAdminUsersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Unauthorized"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        users = User.objects.all()
        serializer = UserSerializer(
            users,
            many=True
        )
        return Response(serializer.data)




class ChangeUserRoleView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, user_id):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Unauthorized"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            user = User.objects.get(
                id=user_id
            )
        except User.DoesNotExist:
            return Response(
                {
                    "error": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        role = request.data.get(
            "role"
        )
        user.role = role
        user.save()
        return Response(
            {
                "message": "Role updated"
            }
        )

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        if not password or not (email or username):
            return Response(
                {"error": "Invalid Credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if email:
            user_record = User.objects.filter(
                email__iexact=email
            ).first()
        else:
            user_record = User.objects.filter(
                username=username
            ).first()

        if not user_record:
            return Response(
                {"error": "Invalid Credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request=request,
            username=user_record.username,
            password=password
        )

        if not user:
            return Response(
                {"error": "Invalid Credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_blocked:
            return Response(
                { "error": "Your account has been blocked" },
                status=403
            )
        
        refresh = RefreshToken.for_user(user)
        send_login_email.delay(
            user.email
        )

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })

class BlockUserView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            user = User.objects.get(
                id=user_id
            )

        except User.DoesNotExist:

            return Response(
                {"error": "User not found"},
                status=404
            )

        if user.role == "company_admin":

            return Response(
                {
                    "error":
                    "Company Admin cannot be blocked"
                },
                status=400
            )

        user.is_blocked = True

        user.save()

        return Response({
            "message": "User blocked successfully"
        })
    

class CompanyUsersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:

            return Response(
                {
                    "error": "Unauthorized"
                },
                status=403
            )

        companies = Tenant.objects.all()

        data = []

        for company in companies:

            admin = User.objects.filter(
                tenant=company,
                role="company_admin"
            ).first()

            users = User.objects.filter(
                tenant=company
            )

            user_data = []

            for user in users:

                user_data.append({

                    "id": user.id,

                    "username": user.username,

                    "email": user.email,

                    "role": user.role,

                    "blocked": user.is_blocked,
                })

            data.append({

                "company_id":
                company.id,

                "company_name":
                company.company_name,

                "admin":
                admin.username if admin else "No Admin",

                "users":
                user_data,
            })

        return Response(data)
    
class CompanySummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:

            return Response(
                {
                    "error": "Unauthorized"
                },
                status=403
            )

        companies = Tenant.objects.all()

        data = []

        for company in companies:

            admin = User.objects.filter(
                tenant=company,
                role="company_admin"
            ).first()

            total_users = User.objects.filter(
                tenant=company
            ).count()

            data.append({

                "id": company.id,

                "company_name": company.company_name,

                "admin":
                admin.username
                if admin
                else "No Admin",

                "total_users":
                total_users,

                "status":
                company.status,
            })

        return Response(data)
    
class CompanyUsersByCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            company = Tenant.objects.get(
                id=company_id
            )

        except Tenant.DoesNotExist:

            return Response(
                {
                    "error": "Company not found"
                },
                status=404
            )

        users = User.objects.filter(
            tenant=company
        )

        data = []

        for user in users:

            data.append({

                "id": user.id,

                "username": user.username,

                "email": user.email,

                "role": user.role,

                "blocked": user.is_blocked,
            })

        return Response({

            "company_name":
            company.company_name,

            "users":
            data
        })
    
class UnblockUserView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):

        if not request.user.is_superuser:

            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            user = User.objects.get(
                id=user_id
            )

        except User.DoesNotExist:

            return Response(
                {"error": "User not found"},
                status=404
            )

        user.is_blocked = False

        user.save()

        return Response({
            "message": "User unblocked successfully"
        })