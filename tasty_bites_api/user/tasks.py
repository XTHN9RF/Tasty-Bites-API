from celery import shared_task
from django.core.mail import send_mail
import os
from dotenv import load_dotenv

from user.models import User


@shared_task
def send_email_task(username: str, mail_subject: str, mail_message: str) -> None:
    load_dotenv()

    user = User.objects.get(username=username)

    send_mail(mail_subject,
              mail_message,
              os.getenv('EMAIL_HOST_USER'),
              [user.email],
              fail_silently=False)
