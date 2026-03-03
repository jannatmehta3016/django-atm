# # atm/utils.py
# from django.core.mail import send_mail
# from django.conf import settings

# def send_wrong_pin_email(account):
#     """
#     Sends an email to the user whenever a wrong PIN attempt is made.
#     """
#     subject = "ATM Alert: Wrong PIN Attempt"
#     message = (
#         f"Dear {account.holder_name},\n\n"
#         f"There was a wrong PIN attempt on your account {account.account_id}.\n"
#         f"Total failed attempts: {account.failed_attempts}\n"
#         "If this was not you, please contact your bank immediately.\n\n"
#         "Regards,\nSBI ATM"
#     )
#     recipient = [account.email]  # Make sure your Account model has 'email' field
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from twilio.rest import Client
from django.conf import settings

def send_sms(to_number, message):
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to="+918295318197"
        )

        print("SMS sent successfully")

    except Exception as e:
        print("SMS failed:", e)
def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"

def hash_otp(otp: str) -> str:
    return make_password(otp)

def verify_otp(raw_otp: str, otp_hash: str) -> bool:
    return check_password(raw_otp, otp_hash)

def otp_expiry(minutes=3):
    return timezone.now() + timedelta(minutes=minutes)