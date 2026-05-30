from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    tenant_name = serializers.CharField(
        source='tenant.company_name',
        read_only=True
    )

    tenant_business_type = serializers.CharField(
        source='tenant.business_type',
        read_only=True
    )

    modules = serializers.JSONField(
        source='tenant.modules',
        read_only=True
    )

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'email',
            'role',
            'tenant',
            'tenant_name',
            'tenant_business_type',
            'modules'
        ]
