# atm/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_wrong_pin_email(account):
    """
    Sends an email to the user whenever a wrong PIN attempt is made.
    """
    subject = "ATM Alert: Wrong PIN Attempt"
    message = (
        f"Dear {account.holder_name},\n\n"
        f"There was a wrong PIN attempt on your account {account.account_number}.\n"
        f"Total failed attempts: {account.failed_attempts}\n"
        "If this was not you, please contact your bank immediately.\n\n"
        "Regards,\nSBI ATM"
    )
    recipient = [account.email]  # Make sure your Account model has 'email' field
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)