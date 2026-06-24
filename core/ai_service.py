import requests

from products.models import Product


def ask_ai(company_id, question):

    products = Product.objects.filter(
        tenant_id=company_id
    )

    product_context = ""

    for product in products:

        product_context += f"""
Product Name: {product.name}
Price: {product.price}
Description: {product.description}

"""

    response = requests.post(
        "http://host.docker.internal:8001/chat",
        json={
            "company_id": company_id,
            "question": question,
            "products": product_context
        }
    )

    return response.json()