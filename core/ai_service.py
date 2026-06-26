import requests

from products.models import Product
from products.models import Order
from accounts.models import User


def ask_ai(
    company_id,
    question,
    user_id=None
):

    products = Product.objects.filter(
        tenant_id=company_id
    )

    product_context = ""

    for product in products:

        product_context += f"""
Product Name: {product.name}
Category: {product.category}
Price: {product.price}
Stock: {product.stock}
Description: {product.description}
"""

    order_context = ""

    orders = Order.objects.filter(
        tenant_id=company_id
    )

    total_revenue = 0

    for order in orders:

        total_revenue += float(
            order.total_price
        )

        order_context += f"""
Customer: {order.user.username}
Product: {order.product.name}
Quantity: {order.quantity}
Price: {order.total_price}
Status: {order.status}
"""

    analytics_context = f"""
Total Orders: {orders.count()}
Total Revenue: {total_revenue}
"""

    customer_context = ""

    customers = User.objects.filter(
        tenant_id=company_id,
        role="customer"
    )

    for customer in customers:

        customer_orders = Order.objects.filter(
            user=customer
        ).count()

        customer_context += f"""
Customer: {customer.username}
Orders: {customer_orders}
"""

    response = requests.post(
        "http://host.docker.internal:8001/chat",
        json={
            "company_id": company_id,
            "question": question,
            "products": product_context,
            "orders": order_context,
            "analytics": analytics_context,
            "customers": customer_context
        }
    )

    return response.json()