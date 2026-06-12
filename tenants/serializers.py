from rest_framework import serializers
from datetime import date
from .models import Tenant
from .models import SubscriptionPayment


class TenantRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    confirm_password = serializers.CharField(
        write_only=True
    )


    class Meta:

        model = Tenant

        fields = [

            'company_name',
            'owner_name',
            'company_email',
            'phone_number',
            'address',
            'business_type',
            'password',
            'confirm_password',
        ]


    def validate(self, data):

        if data['password'] != data['confirm_password']:

            raise serializers.ValidationError(

                "Passwords do not match"
            )

        return data


    def create(self, validated_data):

        validated_data.pop('password')

        validated_data.pop('confirm_password')


        tenant = Tenant.objects.create(

            **validated_data
        )

        return tenant

class TenantSerializer(serializers.ModelSerializer):

    class Meta:

        model = Tenant

        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):

    days_remaining = serializers.SerializerMethodField()

    class Meta:

        model = Tenant

        fields = [

            "company_name",
            "subscription_plan",
            "subscription_start",
            "subscription_end",
            "days_remaining",
            "auto_renew",
            "is_trial_used",
        ]

    def get_days_remaining(self, obj):

        if not obj.subscription_end:

            return 0

        return (
            obj.subscription_end -
            date.today()
        ).days
    

class SubscriptionPaymentSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = SubscriptionPayment

        fields = "__all__"

from rest_framework import serializers
from .models import Tenant


class TenantDropdownSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Tenant

        fields = [
            "id",
            "company_name"
        ]