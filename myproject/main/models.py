from django.db import models
from decimal import Decimal


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
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

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