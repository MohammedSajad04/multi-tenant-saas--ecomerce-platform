from django.db import models
from tenants.models import Tenant


class ChatHistory(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question