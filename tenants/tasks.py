from celery import shared_task

from django.core.mail import send_mail

from django.conf import settings


@shared_task
def send_company_approval_email(
    company_name,
    company_email,
    username,
    password
):

    send_mail(
        subject="Company Approved Successfully",
        message=f"""
Congratulations!

Your company has been approved.

Company Name:
{company_name}

Login Email:
{company_email}

Username:
{username}

Temporary Password:
{password}

Please login and change your password.

Thank You.
        """,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[company_email],
        fail_silently=False
    )

    return "Approval Email Sent"