"""Notifiers: each takes (title, message)."""
import os
import smtplib
import urllib.request
from email.message import EmailMessage


def console(title, message):
    print(f"\n*** {title} ***\n{message}\n")


def ntfy(title, message):
    """Push notification to your phone via https://ntfy.sh (set NTFY_TOPIC)."""
    topic = os.environ["NTFY_TOPIC"]
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
    req = urllib.request.Request(
        f"{server}/{topic}", data=message.encode(), headers={"Title": title, "Tags": "airplane"}
    )
    urllib.request.urlopen(req, timeout=15).close()


def email(title, message):
    """Needs SMTP_HOST, SMTP_USER, SMTP_PASSWORD, EMAIL_TO (SMTP_PORT optional, default 587)."""
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = title, os.environ["SMTP_USER"], os.environ["EMAIL_TO"]
    msg.set_content(message)
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", 587))) as s:
        s.starttls()
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        s.send_message(msg)


NOTIFIERS = {"console": console, "ntfy": ntfy, "email": email}
