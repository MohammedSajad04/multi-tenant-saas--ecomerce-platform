from rest_framework import serializers

from .models import Tenant



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
