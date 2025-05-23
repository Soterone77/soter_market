from email.message import EmailMessage

from pydantic import EmailStr

from app.core.config import settings


def create_register_confirmation_template(
    email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Подтверждение регистрации"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Вы совершили регистрацию на Soter Market</h1>
        """,
        subtype="html",
    )
    return email
