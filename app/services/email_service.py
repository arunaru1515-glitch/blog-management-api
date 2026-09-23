import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def send_email(
    to_email: str,
    subject: str,
    body: str
):
    sender_email = os.getenv("EMAIL_ADDRESS")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not smtp_username or not smtp_password:
        print("Email configuration is missing")
        return

    message = EmailMessage()

    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    email_body = (
        f"{body}\n\n"
        f"Timestamp: {timestamp}\n\n"
        f"Blog Management API"
    )

    message.set_content(email_body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(message)

        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Email sending failed: {e}")
