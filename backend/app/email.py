# app/email.py

import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode
import threading

from app.core.config import settings


def build_verification_link(token: str) -> str:
    base = settings.FRONTEND_URL or "http://localhost:3000"
    query = urlencode({"token": token})
    return f"{base}/verify-email?{query}"


def send_verification_email(to_email: str, token: str) -> None:
    link = build_verification_link(token)

    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(f"Click this link to verify your email: {link}")

    if not settings.SMTP_HOST:
        # fallback debug mode
        print("=== EMAIL (DEBUG) ===")
        print("To:", to_email)
        print("Subject: Verify your email")
        print("Body:", msg.get_content())
        print("=====================")
        return

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_task_assignment_email(to_email: str, assignee_name: str, task_desc: str, topic: str):
    msg = EmailMessage()
    msg["Subject"] = f"Action Required: {topic}"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    
    body = (
        f"Hi {assignee_name or to_email.split('@')[0]},\n\n"
        f"You have a new action item assigned to you from the meeting '{topic}':\n\n"
        f"✅ Task: {task_desc}\n\n"
        f"Please check your Darwin workspace for more details.\n"
    )
    msg.set_content(body)

    def _send():
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send task email to {to_email}: {e}")

    # Fire and forget
    threading.Thread(target=_send, daemon=True).start()
