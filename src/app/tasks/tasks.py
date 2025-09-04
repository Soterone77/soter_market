import smtplib

from pydantic import EmailStr

from app.core.config import settings
from app.logger import logger
from app.tasks.celery_app import celery
from app.tasks.email_templates import create_register_confirmation_template


@celery.task
def send_registration_confirmation_email(
    email_to: EmailStr,
):
    # Удалите строчку ниже для отправки сообщения на свой email, а на пользовательский
    email_to = settings.SMTP_USER
    msg_content = create_register_confirmation_template(email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    logger.info(f"Successfully send email message to {email_to}")
