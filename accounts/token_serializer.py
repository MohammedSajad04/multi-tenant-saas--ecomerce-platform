from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    email = serializers.EmailField()

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        try:

            user = User.objects.get(
                email=email
            )

        except User.DoesNotExist:

            raise serializers.ValidationError(
                "Invalid email or password"
            )

        attrs["username"] = user.username

        data = super().validate(attrs)

        if (
            user.role == "company_admin"
            and user.tenant
            and user.tenant.status != "approved"
        ):

            raise serializers.ValidationError(
                "Your company account has been blocked or not approved."
            )

        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }

        return data