from django.utils import timezone
from datetime import timedelta
from main.models import Transaction


def check_transaction(account, amount):
    """
    Returns True if suspicious
    Returns False if safe
    """

    now = timezone.now()

    # RULE 1 — too many transactions in 1 minute
    recent_transactions = Transaction.objects.filter(
        account=account,
        timestamp__gte=now - timedelta(minutes=1),
        transaction_type="WITHDRAW"
    )

    if recent_transactions.count() >= 3:
        print("Too many transactions in 1 minute")
        return True

    # RULE 2 — sudden large withdrawal
    past_transactions = Transaction.objects.filter(
        account=account,
        transaction_type="WITHDRAW"
    )

    if past_transactions.exists():
        avg = sum(t.amount for t in past_transactions) / past_transactions.count()

        if amount > avg * 3:
            print("sudden large withdrawl")
            return True

    # RULE 3 — rapid withdrawals (<50 sec)
    last_txn = Transaction.objects.filter(
        account=account,
        transaction_type="WITHDRAW"
    ).order_by("-timestamp").first()

    if last_txn:
        gap = (now - last_txn.timestamp).total_seconds()
        if gap < 50:
            print("rapid withdrawls")
            return True

    return False