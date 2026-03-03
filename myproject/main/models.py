from django.db import models
from decimal import Decimal
from django.utils import timezone


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = (
        ('SAVINGS', 'Savings Account'),
        ('CURRENT', 'Current Account'),
    )

    account_id = models.IntegerField(unique=True)  # Only ID we use
    card_number = models.CharField(max_length=16, unique=True, null=True, blank=True)
    holder_name = models.CharField(max_length=100)
    pin = models.CharField(max_length=4)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qr_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    failed_attempts = models.IntegerField(default=0)
    block_count = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    is_permanent_block = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def deposit(self, amount):
        amount = Decimal(str(amount))
        if amount > 0:
            self.balance += amount
            self.save()
            return True
        return False

    def verify_pin(self, pin):
        
        return self.pin == pin

    def set_pin(self, new_pin):
        self.pin = new_pin
        self.save(update_fields=['pin'])

    def withdraw(self, amount):
        amount = Decimal(str(amount))

        if self.account_type == 'SAVINGS':
            min_balance = Decimal('500')
            if self.balance - amount >= min_balance:
                self.balance -= amount
                self.save()
                return True
            return False

        elif self.account_type == 'CURRENT':
            overdraft = Decimal('1000')
            if self.balance + overdraft >= amount:
                self.balance -= amount
                self.save()
                return True
            return False

        return False

    def __str__(self):
        return f"{self.account_id} - {self.holder_name}"


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('TRANSFER', 'Transfer'),
    )
    STATUS_COMPLETED = "COMPLETED"
    STATUS_PENDING_OTP = "PENDING_OTP"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_COMPLETED, "Completed"),
        (STATUS_PENDING_OTP, "Pending OTP"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED
    )


    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    is_fraud = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account.holder_name} - {self.transaction_type} - {self.amount}"
    
class OtpChallenge(models.Model):
        account = models.ForeignKey(
            "Account",
            on_delete=models.CASCADE
        )

        transaction = models.OneToOneField(
            "Transaction",
            on_delete=models.CASCADE,
            related_name="otp_challenge"
        )

        otp_hash = models.CharField(max_length=128)

        expires_at = models.DateTimeField()

        attempts = models.PositiveSmallIntegerField(default=0)

        max_attempts = models.PositiveSmallIntegerField(default=3)

        is_used = models.BooleanField(default=False)

        created_at = models.DateTimeField(auto_now_add=True)

        def is_expired(self):
            return timezone.now() >= self.expires_at