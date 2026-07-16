"""Email verification service using SMTP (QQ Mail).

Sends verification codes via email and stores them with expiration for validation.
"""

import random
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

from app.config import settings


# In-memory verification code storage: {email: (code, expire_timestamp)}
_code_store: dict[str, tuple[str, float]] = {}


def generate_code() -> str:
    """Generate a 6-digit verification code."""
    return f"{random.randint(100000, 999999)}"


def send_verification_email(to_email: str, code: str) -> bool:
    """Send a verification code email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_USER))
    msg["To"] = to_email
    msg["Subject"] = Header("减脂PK - 验证码", "utf-8")

    html_content = f"""
    <div style="max-width:400px;margin:0 auto;font-family:sans-serif;">
        <div style="background:#007aff;color:#fff;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
            <h2 style="margin:0;">减脂PK</h2>
        </div>
        <div style="background:#fff;padding:30px;border:1px solid #e0e0e0;border-radius:0 0 8px 8px;text-align:center;">
            <p style="color:#333;font-size:14px;">您的验证码是：</p>
            <p style="font-size:32px;font-weight:bold;color:#007aff;letter-spacing:8px;margin:20px 0;">{code}</p>
            <p style="color:#999;font-size:12px;">验证码 {settings.VERIFICATION_CODE_EXPIRE_MINUTES} 分钟内有效，请勿泄露给他人。</p>
        </div>
    </div>
    """
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send to {to_email}: {e}")
        raise


def send_code(to_email: str) -> str:
    """Generate, store, and send a verification code to the given email."""
    code = generate_code()
    expire_ts = time.time() + settings.VERIFICATION_CODE_EXPIRE_MINUTES * 60
    _code_store[to_email] = (code, expire_ts)
    
    # If SMTP settings are missing, log code to console and succeed (dev mode helper)
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"\n[DEVELOPMENT VERIFICATION CODE] Email: {to_email} | Code: {code}\n")
        return code

    try:
        send_verification_email(to_email, code)
    except Exception as e:
        print(f"[Email Warning] Could not send email via SMTP, printing to console: {e}")
        print(f"\n[DEVELOPMENT VERIFICATION CODE] Email: {to_email} | Code: {code}\n")
    return code


def verify_code(email: str, code: str) -> bool:
    """Verify the code for the given email. Returns True if valid."""
    stored = _code_store.get(email)
    if stored is None:
        return False
    stored_code, expire_ts = stored
    # Check expiration
    if time.time() > expire_ts:
        del _code_store[email]
        return False
    # Check code match
    if stored_code != code:
        return False
    # Code is valid, remove it (one-time use)
    del _code_store[email]
    return True


def send_reset_password_email(to_email: str, reset_link: str) -> bool:
    """Send a password reset link email."""
    # Check if SMTP settings are configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"\n[DEVELOPMENT RESET LINK] Email: {to_email} | Link: {reset_link}\n")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_USER))
    msg["To"] = to_email
    msg["Subject"] = Header("减脂PK - 重置密码请求", "utf-8")

    html_content = f"""
    <div style="max-width:400px;margin:0 auto;font-family:sans-serif;">
        <div style="background:#ff3b30;color:#fff;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
            <h2 style="margin:0;">减脂PK</h2>
        </div>
        <div style="background:#fff;padding:30px;border:1px solid #e0e0e0;border-radius:0 0 8px 8px;text-align:center;">
            <p style="color:#333;font-size:14px;">您收到此邮件是因为您申请重置密码。</p>
            <p style="color:#333;font-size:14px;">请点击下方链接，系统将自动将您的密码重置为 <strong>123456</strong>：</p>
            <p style="margin:25px 0;">
                <a href="{reset_link}" style="background:#ff3b30;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold;font-size:14px;">立即重置密码</a>
            </p>
            <p style="color:#999;font-size:11px;">此链接 15 分钟内有效。如果您没有请求重置密码，请忽略此邮件。</p>
        </div>
    </div>
    """
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send reset email to {to_email}: {e}")
        # Fallback to printing in console
        print(f"\n[DEVELOPMENT RESET LINK FALLBACK] Email: {to_email} | Link: {reset_link}\n")
        return True

