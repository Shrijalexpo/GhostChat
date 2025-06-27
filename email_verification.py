import os
import smtplib
import random
import ssl
import re
from email.message import EmailMessage
from log import log

# Email credentials
SENDER_EMAIL = 'ghostchatbot@gmail.com'
SENDER_PASSWORD = 'cujw ozkz tigk duam'


# Dictionary to store OTPs for verification
otp_storage = {}

def is_valid_email(email):
    """Validate email format"""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None

def extract_domain(email):
    """Extract domain from email address"""
    return email.split("@")[1] if "@" in email else None

def generate_otp():
    """Generate a 6-digit OTP"""
    return "GC-" + str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    """Send OTP via email"""
    subject = "Your OTP Verification Code - GhostChat"
    body = f"Your OTP code is: {otp} \n \n Warm Regards,\nTeam GhostChat"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        log(f"OTP sent to email: {receiver_email}")
        return True
    except Exception as e:
        log(f"Error sending OTP email: {e}")
        return False

def store_otp(chat_id, email, otp):
    """Store OTP for verification"""
    otp_storage[str(chat_id)] = {
        "email": email,
        "otp": otp,
        "verified": False
    }

def verify_otp(chat_id, user_input_otp):
    """Verify the OTP entered by user"""
    chat_id_str = str(chat_id)
    if chat_id_str in otp_storage:
        stored_otp = otp_storage[chat_id_str]["otp"]
        if stored_otp == user_input_otp:
            otp_storage[chat_id_str]["verified"] = True
            return True
    return False

def get_verified_email(chat_id):
    """Get verified email for a chat_id"""
    chat_id_str = str(chat_id)
    if chat_id_str in otp_storage and otp_storage[chat_id_str]["verified"]:
        return otp_storage[chat_id_str]["email"]
    return None

def clear_otp_data(chat_id):
    """Clear OTP data after successful verification"""
    chat_id_str = str(chat_id)
    if chat_id_str in otp_storage:
        email = otp_storage[chat_id_str]["email"]
        del otp_storage[chat_id_str]
        return email
    return None