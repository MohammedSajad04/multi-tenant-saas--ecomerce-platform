from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:

        model = Order

        fields = "__all__"

        read_only_fields = [
            'tenant',
            'user',
            'total_price'
        ]