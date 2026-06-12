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
        password = request.data.get("password")
        try:
            user = User.objects.get(
                email=email
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid Credentials"},
                status=400
            )
        user = authenticate(
            username=user.username,
            password=password
        )
        if not user:
            return Response(
                {"error": "Invalid Credentials"},
                status=400
            )
        refresh = RefreshToken.for_user(user)
        send_login_email.delay(
            user.email
        )
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })