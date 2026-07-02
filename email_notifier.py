import smtplib
from email.mime.text import MIMEText

from config import (
    EMAIL_ENABLED,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_SENDER,
    EMAIL_PASSWORD
)

from database import get_all_user_emails


def send_email_to_all_users(subject, message):

    if not EMAIL_ENABLED:
        print("[EMAIL] Notificari dezactivate.")
        return

    receivers = get_all_user_emails()

    if not receivers:
        print("[EMAIL] Nu exista utilizatori.")
        return

    email = MIMEText(
        message,
        "plain",
        "utf-8"
    )

    email["Subject"] = subject
    email["From"] = EMAIL_SENDER
    email["To"] = ", ".join(receivers)

    try:

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                EMAIL_SENDER,
                EMAIL_PASSWORD
            )

            server.send_message(email)

        print(
            f"[EMAIL] Trimis catre {len(receivers)} utilizatori."
        )

    except Exception as error:

        print(
            f"[EMAIL ERROR] {error}"
        )
def send_password_reset_email(receiver_email, reset_link):

    if not EMAIL_ENABLED:
        print("[EMAIL] Notificari dezactivate.")
        print(f"[RESET LINK] {reset_link}")
        return

    subject = "Resetare parola - Sistem supraveghere"

    message = f"""
Buna,

Ai solicitat resetarea parolei pentru contul tau.

Pentru a seta o parola noua, acceseaza linkul de mai jos:

{reset_link}

Daca nu ai solicitat aceasta actiune, ignora acest mesaj.

Linkul este valabil o perioada limitata.
"""

    email = MIMEText(message, "plain", "utf-8")
    email["Subject"] = subject
    email["From"] = EMAIL_SENDER
    email["To"] = receiver_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(email)

        print(f"[EMAIL] Link resetare trimis catre {receiver_email}")

    except Exception as error:
        print(f"[EMAIL ERROR] {error}")

def send_surveillance_alert(message):
    subject = "Alertă sistem supraveghere"

    send_email_to_all_users(
        subject,
        message
    )
