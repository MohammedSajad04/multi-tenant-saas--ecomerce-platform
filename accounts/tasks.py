from celery import shared_task

from django.core.mail import send_mail

from django.conf import settings


@shared_task
def send_login_email(email):

    send_mail(
        subject='Login Alert',
        message='You have successfully logged into the SaaS Platform.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

    return "Email Sent"