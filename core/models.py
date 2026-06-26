from django.db import models

from tenants.models import Tenant
from accounts.models import User


class ChatHistory(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.question