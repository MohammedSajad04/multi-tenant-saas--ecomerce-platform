from django.db import models

from tenants.models import Tenant

from accounts.models import User



class Product(models.Model):

    BUSINESS_TYPE_CHOICES = (

        ('mobile', 'Mobile Store'),
        ('cake', 'Cake Shop'),
        ('perfume', 'Perfume Store'),
    )

    tenant = models.ForeignKey(

        Tenant,
        on_delete=models.CASCADE
    )

    name = models.CharField(

        max_length=255
    )

    description = models.TextField()

    category = models.CharField(

        max_length=100
    )

    business_type = models.CharField(

        max_length=50,
        choices=BUSINESS_TYPE_CHOICES,
        default='mobile'
    )

    price = models.DecimalField(

        max_digits=10,
        decimal_places=2
    )

    stock = models.IntegerField()

    image = models.ImageField(

        upload_to="products/",

        blank=True,

        null=True
    )

    created_at = models.DateTimeField(

        auto_now_add=True
    )

    def __str__(self):

        return self.name


class Order(models.Model):

    STATUS_CHOICES = (

        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
    )

    tenant = models.ForeignKey(

        Tenant,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(

        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(

        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(

        default=1
    )

    total_price = models.DecimalField(

        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(

        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(

        auto_now_add=True
    )

    def __str__(self):

        return f"{self.user.username} - {self.product.name}"
