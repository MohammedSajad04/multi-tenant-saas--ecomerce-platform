from django.db import models
import uuid


class Tenant(models.Model):

    BUSINESS_CHOICES = (

        ("mobile", "Mobile"),
        ("cake", "Cake"),
        ("perfume", "Perfume"),
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
        default="mobile"
    )

    owner_name = models.CharField(
        max_length=255
    )

    company_email = models.EmailField()

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
        default='pending'
    )

    # ======================
    # SUBSCRIPTION FIELDS
    # ======================

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

    def save(self, *args, **kwargs):

        if not self.registration_number:

            unique_id = str(uuid.uuid4())[:8]

            self.registration_number = (
                f"CMP-{unique_id.upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.company_name