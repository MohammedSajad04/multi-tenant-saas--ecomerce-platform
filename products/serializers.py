from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
    source="tenant.company_name",
    read_only=True
)
    class Meta:

        model = Product

        fields = "__all__"

        read_only_fields = [
            "tenant"
        ]