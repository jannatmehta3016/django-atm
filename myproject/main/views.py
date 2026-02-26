from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from pyzbar.pyzbar import decode
from PIL import Image
from .utils import send_wrong_pin_email 
from ai_engine.fraud_detector import check_transaction

from .models import Account, Transaction

FAST_CASH_AMOUNTS = [100, 200, 500, 1000, 2000, 5000]

# ---------------- Helper Functions ----------------
def is_account_blocked(account):
    """Check if account is blocked and auto-unblock if time passed."""
    if account.is_blocked:
        if account.blocked_until and timezone.now() < account.blocked_until:
            return True
        else:
            account.is_blocked = False
            account.failed_attempts = 0
            account.save()
    return False

# def get_account_with_pin(account_id, pin):
#     """Fetch account by account_id and verify PIN."""
#     try:
#         account = Account.objects.get(id=account_id)
#         if not account.verify_pin(pin):
#             return None
#         return account
#     except Account.DoesNotExist:
#         return None
def get_account_with_pin(account_id, pin):
    try:
        account = Account.objects.get(id=account_id)

        # Check PIN
        if not account.verify_pin(pin):
            # Increment failed attempts
            account.failed_attempts += 1

            # Optional: block account after 3 failed attempts
            if account.failed_attempts >= 3:
                account.is_blocked = True
                account.blocked_until = timezone.now() + timedelta(minutes=15)  # 15 min block

            account.save()

            # Send email notification
            if account.email:
                send_wrong_pin_email(account)

            return None

        # Successful PIN resets failed attempts and unblocks
        account.failed_attempts = 0
        account.is_blocked = False
        account.blocked_until = None
        account.save()

        return account

    except Account.DoesNotExist:
        return None

def get_today_withdraw_total(account):
    today = timezone.now().date()
    return sum(tx.amount for tx in Transaction.objects.filter(account=account, transaction_type="WITHDRAW", timestamp__date=today))

def get_today_withdraw_count(account):
    today = timezone.now().date()
    return Transaction.objects.filter(account=account, transaction_type="WITHDRAW", timestamp__date=today).count()

def get_today_deposit_total(account):
    today = timezone.now().date()
    return sum(tx.amount for tx in Transaction.objects.filter(account=account, transaction_type="DEPOSIT", timestamp__date=today))

# ---------------- QR Login ----------------
@api_view(['POST'])
def qr_login(request):
    file = request.FILES.get("qr")
    if not file:
        return Response({"success": False, "message": "Invalid QR"}, status=400)

    try:
        img = Image.open(file)
    except:
        return Response({"success": False, "message": "Invalid QR"}, status=400)

    decoded = decode(img)
    if not decoded:
        return Response({"success": False, "message": "Invalid QR"}, status=400)

    token = decoded[0].data.decode("utf-8")
    account = Account.objects.filter(qr_token=token).first()
    if not account:
        return Response({"success": False, "message": "Invalid QR"}, status=400)

    # Login successful
    return Response({
        "success": True,
        "message": "QR login successful",
        "data": {"account_id": account.id, "holder_name": account.holder_name}
    })

# ---------------- Operation APIs (PIN per action) ----------------

@api_view(['POST'])
def deposit(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')
    amount = request.data.get('amount')

    if not all([account_id, pin, amount]):
        return Response({"success": False, "message": "account_id, pin and amount are required"}, status=400)

    account = get_account_with_pin(account_id, pin)
    if not account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    try:
        amount = Decimal(amount)
        if amount <= 0:
            return Response({"success": False, "message": "Amount must be greater than 0"}, status=400)
    except:
        return Response({"success": False, "message": "Invalid amount"}, status=400)

    if get_today_deposit_total(account) + amount > 50000:
        return Response({"success": False, "message": "Daily deposit limit exceeded (50000)"}, status=400)

    account.deposit(amount)
    Transaction.objects.create(account=account, transaction_type='DEPOSIT', amount=amount, remark='ATM Deposit')

    # Session ends after action
    return Response({
        "success": True,
        "message": "Deposit successful, session ended",
        "data": {"balance": account.balance}
    })

# @api_view(['POST'])
# def withdraw(request):
#     account_id = request.data.get('account_id')
#     pin = request.data.get('pin')
#     amount = request.data.get('amount')

#     account = get_account_with_pin(account_id, pin)
#     if not account:
#         return Response({"success": False, "message": "Invalid PIN"}, status=403)

#     if is_account_blocked(account):
#         return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

#     try:
#         amount = Decimal(amount)
#     except:
#         return Response({"success": False, "message": "Invalid amount"}, status=400)

#     if amount > 10000:
#         return Response({"success": False, "message": "Maximum withdrawal per transaction is 10000"}, status=400)

#     if get_today_withdraw_count(account) >= 5:
#         return Response({"success": False, "message": "Maximum 5 withdrawals per day allowed"}, status=400)

#     if get_today_withdraw_total(account) + amount > 40000:
#         return Response({"success": False, "message": "Daily withdrawal limit reached (40000)"}, status=400)

#     if not account.withdraw(amount):
#         return Response({"success": False, "message": "Insufficient balance"}, status=400)

#     Transaction.objects.create(account=account, transaction_type='WITHDRAW', amount=amount, remark='ATM Withdraw')

#     # Session ends after action
#     return Response({
#         "success": True,
#         "message": "Withdrawal successful, session ended",
#         "data": {"withdrawn": amount, "balance": account.balance}
#     })
@api_view(['POST'])
def withdraw(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')
    amount = request.data.get('amount')

    account = get_account_with_pin(account_id, pin)
    if not account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    try:
        amount = Decimal(amount)
    except:
        return Response({"success": False, "message": "Invalid amount"}, status=400)

    if amount > 10000:
        return Response({"success": False, "message": "Maximum withdrawal per transaction is 10000"}, status=400)

    if get_today_withdraw_count(account) >= 10:
        return Response({"success": False, "message": "Maximum 5 withdrawals per day allowed"}, status=400)

    if get_today_withdraw_total(account) + amount > 40000:
        return Response({"success": False, "message": "Daily withdrawal limit reached (40000)"}, status=400)

    # 🧠 AI FRAUD DETECTOR
    if check_transaction(account, amount):
        return Response({
            "success": False,
            "message": "Suspicious activity detected. Transaction blocked."
        }, status=403)

    if not account.withdraw(amount):
        return Response({"success": False, "message": "Insufficient balance"}, status=400)

    Transaction.objects.create(
        account=account,
        transaction_type='WITHDRAW',
        amount=amount,
        remark='ATM Withdraw'
    )

    return Response({
        "success": True,
        "message": "Withdrawal successful, session ended",
        "data": {"withdrawn": amount, "balance": account.balance}
    })

@api_view(['POST'])
def balance_inquiry(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')

    account = get_account_with_pin(account_id, pin)
    if not account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    # Session ends after action
    return Response({
        "success": True,
        "message": "Balance fetched successfully, session ended",
        "data": {"balance": account.balance, "holder_name": account.holder_name}
    })

@api_view(['POST'])
def mini_statement(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')

    account = get_account_with_pin(account_id, pin)
    if not account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    transactions = account.transactions.order_by('-timestamp')[:5]
    data = [{"type": tx.transaction_type, "amount": tx.amount, "timestamp": tx.timestamp, "remark": tx.remark} for tx in transactions]

    # Session ends after action
    return Response({
        "success": True,
        "message": "Mini statement fetched, session ended",
        "data": {"transactions": data}
    })

@api_view(['POST'])
def fast_cash(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')
    amount = request.data.get('amount')

    account = get_account_with_pin(account_id, pin)
    if not account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    try:
        amount = int(amount)
    except:
        return Response({"success": False, "message": "Invalid amount"}, status=400)

    if amount not in FAST_CASH_AMOUNTS:
        return Response({"success": False, "message": "Invalid fast cash amount"}, status=400)

    if not account.withdraw(amount):
        return Response({"success": False, "message": "Insufficient balance"}, status=400)

    Transaction.objects.create(account=account, transaction_type='WITHDRAW', amount=amount, remark='Fast Cash')

    # Session ends after action
    return Response({
        "success": True,
        "message": "Fast cash successful, session ended",
        "data": {"balance": account.balance}
    })

@api_view(['POST'])
def change_pin(request):
    account_id = request.data.get('account_id')
    old_pin = request.data.get('old_pin')
    new_pin = request.data.get('new_pin')

    if not all([account_id, old_pin, new_pin]):
        return Response({"success": False, "message": "All fields are required"}, status=400)

    account = get_account_with_pin(account_id, old_pin)
    if not account:
        return Response({"success": False, "message": "Invalid old PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    if not new_pin.isdigit() or len(new_pin) != 6:
        return Response({"success": False, "message": "PIN must be a 6-digit number"}, status=400)

    if old_pin == new_pin:
        return Response({"success": False, "message": "New PIN must be different from old PIN"}, status=400)

    account.set_pin(new_pin)

    # Session ends after action
    return Response({"success": True, "message": "PIN changed successfully, session ended"})

@api_view(['POST'])
def transfer_money(request):
    from_account_id = request.data.get("from_account_id")
    to_account_id = request.data.get("to_account_id")
    pin = request.data.get("pin")
    amount = request.data.get("amount")

    if not all([from_account_id, to_account_id, pin, amount]):
        return Response({"success": False, "message": "Missing parameters"}, status=400)

    from_account = get_account_with_pin(from_account_id, pin)
    if not from_account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(from_account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    try:
        to_account = Account.objects.get(id=to_account_id)
    except Account.DoesNotExist:
        return Response({"success": False, "message": "Target account not found"}, status=404)

    if from_account.balance < Decimal(amount):
        return Response({"success": False, "message": "Insufficient funds"}, status=400)

    from_account.balance -= Decimal(amount)
    to_account.balance += Decimal(amount)
    from_account.save()
    to_account.save()

    # Session ends after action
    return Response({"success": True, "message": "Transfer successful, session ended"})