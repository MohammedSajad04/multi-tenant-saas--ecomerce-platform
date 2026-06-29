from django.db import models
import uuid
from django.utils.text import slugify

class Tenant(models.Model):

    BUSINESS_CHOICES = (

        ("ecommerce", "Ecommerce"),
        ("service", "Service"),
        ("hybrid", "Hybrid"),
    )

    STATUS_CHOICES = (

        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    )

    PLAN_CHOICES = (

        ('trial', 'Free Trial'),
        ('monthly', 'Monthly'),
        ('six_month', 'Six Months'),
        ('yearly', 'Yearly'),
    )

    company_name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True
    )

    business_type = models.CharField(
        max_length=50,
        choices=BUSINESS_CHOICES,
        default="ecommerce"
    )

    owner_name = models.CharField(
        max_length=255
    )

    company_email = models.EmailField(
    unique=True
    )

    phone_number = models.CharField(
        max_length=20
    )

    address = models.TextField()

    company_description = models.TextField()

    registration_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    modules = models.JSONField(
        default=list
    )

    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default="pending"
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    blocked_reason = models.TextField(
        blank=True,
        null=True
    )

    deleted_reason = models.TextField(
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )
    subscription_plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="trial"
    )

    subscription_start = models.DateField(
        null=True,
        blank=True
    )

    subscription_end = models.DateField(
        null=True,
        blank=True
    )

    is_trial_used = models.BooleanField(
        default=False
    )

    auto_renew = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    logo = models.ImageField(
        upload_to="company_logos/",
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(
                self.company_name
            )

        if not self.registration_number:

            unique_id = str(uuid.uuid4())[:8]

            self.registration_number = (
                f"CMP-{unique_id.upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.company_name

class SubscriptionPayment(models.Model):

    PLAN_CHOICES = (

        ('monthly', 'Monthly'),
        ('six_month', 'Six Months'),
        ('yearly', 'Yearly'),
    )

    STATUS_CHOICES = (

        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    rejection_reason = models.TextField(
    blank=True,
    null=True
    )
    blocked_reason = models.TextField(
        blank=True,
        null=True
    )

    deleted_reason = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):

        return (
            f"{self.tenant.company_name} - "
            f"{self.plan} - "
            f"{self.status}"
        )
    