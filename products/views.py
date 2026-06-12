from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .order_serializers import OrderSerializer
from .serializers import ProductSerializer
from .models import ( Product, Order )
import razorpay
from django.conf import settings
from datetime import date, timedelta


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not request.user.tenant:
            return Response(
                {
                    "error": "Company account required"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save(
                tenant=request.user.tenant,
                business_type=request.user.tenant.business_type
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class ProductListView(APIView):

    def get(self, request):

        tenant_id = request.GET.get("tenant")

        products = Product.objects.filter(
            tenant_id=tenant_id,
            tenant__status="approved"
        )

        serializer = ProductSerializer(
            products,
            many=True
        )

        return Response(serializer.data)


class CompanyProductsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.tenant:
            return Response(
                {
                    "error": "Company account required"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        products = Product.objects.filter(

            tenant=request.user.tenant
        )

        serializer = ProductSerializer(

            products,
            many=True
        )

        return Response(serializer.data)


class ProductDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product)

        return Response(serializer.data)

    def put(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id,
                tenant=request.user.tenant
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save(
                business_type=request.user.tenant.business_type
            )

            return Response(serializer.data)

        print("========== ERRORS ==========")
        print(serializer.errors)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id,
                tenant=request.user.tenant
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        product.delete()

        return Response(
            {
                "message": "Product deleted successfully"
            }
        )
    
class CreateOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = int(
            request.data.get('quantity', 1)
        )

        if quantity <= 0:

            return Response(
                {
                    "error": "Quantity must be greater than 0"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > product.stock:

            return Response(
                {
                    "error": "Insufficient stock"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        total_price = product.price * quantity

        order = Order.objects.create(

            tenant=product.tenant,

            user=request.user,

            product=product,

            quantity=quantity,

            total_price=total_price
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class CompanyDashboardView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request):

        tenant = request.user.tenant


        total_products = Product.objects.filter(

            tenant=tenant
        ).count()


        total_orders = Order.objects.filter(

            tenant=tenant
        ).count()


        total_revenue = sum(

            order.total_price

            for order in Order.objects.filter(
                tenant=tenant
            )
        )


        recent_orders = Order.objects.filter(

            tenant=tenant

        ).order_by(

            '-created_at'
        )[:5]


        recent_orders_data = []


        for order in recent_orders:

            recent_orders_data.append({

                "product": order.product.name,

                "customer": order.user.username,

                "quantity": order.quantity,

                "total_price": order.total_price,

                "status": order.status,
            })


        return Response({

            "total_products": total_products,

            "total_orders": total_orders,

            "total_revenue": total_revenue,

            "recent_orders": recent_orders_data,
        })
    

class CompanyOrdersView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request):

        tenant = request.user.tenant


        orders = Order.objects.filter(

            tenant=tenant

        ).order_by(

            '-created_at'
        )


        orders_data = []


        for order in orders:

            orders_data.append({

                "id": order.id,

                "customer": order.user.username,

                "customer_email": order.user.email,

                "product": order.product.name,

                "quantity": order.quantity,

                "total_price": order.total_price,

                "status": order.status,
            })


        return Response(orders_data)

class CompanyCustomersView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request):

        tenant = request.user.tenant


        orders = Order.objects.filter(

            tenant=tenant
        )


        customers = []


        added_users = set()


        for order in orders:

            if order.user.id not in added_users:

                customers.append({

                    "id": order.user.id,

                    "username": order.user.username,

                    "email": order.user.email,
                })

                added_users.add(order.user.id)


        return Response(customers)

class MyOrdersView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)
    
class UpdateOrderStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, order_id):

        order = Order.objects.get(
            id=order_id,
            tenant=request.user.tenant
        )

        order.status = request.data.get(
            'status'
        )

        order.save()

        return Response({
            "message": "Status Updated"
        })
    def get(self, request, product_id):

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product)

        return Response(serializer.data)
    

class CreateOrderPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        razorpay_order = client.order.create({
            "amount": int(order.total_price * 100),
            "currency": "INR",
            "payment_capture": 1,
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        return Response({
            "db_order_id": order.id,
            "order_id": razorpay_order["id"],
            "amount": int(order.total_price * 100),
            "key": settings.RAZORPAY_KEY_ID,
        })
    

class VerifyOrderPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        order = Order.objects.get(
            id=request.data.get("db_order_id")
        )

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:

            client.utility.verify_payment_signature({

                "razorpay_order_id":
                request.data.get("razorpay_order_id"),

                "razorpay_payment_id":
                request.data.get("razorpay_payment_id"),

                "razorpay_signature":
                request.data.get("razorpay_signature"),

            })

        except:

            return Response(
                {"error": "Payment Failed"},
                status=400
            )

        order.payment_status = "paid"
        order.status = "confirmed"

        product = order.product

        product.stock -= order.quantity

        product.save()

        order.razorpay_payment_id = (
            request.data.get(
                "razorpay_payment_id"
            )
        )

        order.save()

        return Response({
            "message": "Payment Successful"
        })
