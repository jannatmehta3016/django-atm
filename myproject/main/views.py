from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db import transaction as db_transaction
from rest_framework.decorators import api_view
from pyzbar.pyzbar import decode
from PIL import Image
# from .utils import send_wrong_pin_email 
from .utils import send_sms
from ai_engine.fraud_detector import check_transaction
from .models import Transaction, OtpChallenge
from .utils import generate_otp, hash_otp, otp_expiry

from .models import Account, Transaction
from decimal import Decimal

OTP_THRESHOLD = Decimal("10000")

FAST_CASH_AMOUNTS = [100, 200, 500, 1000, 2000, 5000]

# ---------------- Helper Functions ----------------



@api_view(['POST'])
def verify_withdraw_otp(request):
    transaction_id = request.data.get("transaction_id")
    otp = str(request.data.get("otp") or "").strip()

    # 1️⃣ Basic validation
    if not transaction_id or not otp:
        return Response({
            "success": False,
            "message": "transaction_id and otp are required"
        }, status=400)

    # 2️⃣ Fetch transaction
    txn = Transaction.objects.select_related("account").filter(id=transaction_id).first()
    if not txn:
        return Response({
            "success": False,
            "message": "Transaction not found"
        }, status=404)

    # 3️⃣ Ensure transaction is waiting for OTP
    if txn.status != Transaction.STATUS_PENDING_OTP:
        return Response({
            "success": False,
            "message": f"Transaction not pending OTP (status={txn.status})"
        }, status=400)

    # 4️⃣ Fetch OTP challenge
    challenge = getattr(txn, "otp_challenge", None)
    if not challenge:
        return Response({
            "success": False,
            "message": "OTP challenge not found"
        }, status=400)

    # 5️⃣ Check OTP state
    if challenge.is_used:
        return Response({
            "success": False,
            "message": "OTP already used"
        }, status=400)

    if challenge.is_expired():
        txn.status = Transaction.STATUS_CANCELLED
        txn.save(update_fields=["status"])
        return Response({
            "success": False,
            "message": "OTP expired. Transaction cancelled."
        }, status=400)

    if challenge.attempts >= challenge.max_attempts:
        txn.status = Transaction.STATUS_CANCELLED
        txn.save(update_fields=["status"])
        return Response({
            "success": False,
            "message": "Maximum OTP attempts exceeded. Transaction cancelled."
        }, status=403)

    # 6️⃣ Verify OTP
    from .utils import verify_otp

    if not verify_otp(otp, challenge.otp_hash):
        challenge.attempts += 1
        challenge.save(update_fields=["attempts"])

        remaining = challenge.max_attempts - challenge.attempts

        if remaining <= 0:
            txn.status = Transaction.STATUS_CANCELLED
            txn.save(update_fields=["status"])
            return Response({
                "success": False,
                "message": "Incorrect OTP. Transaction cancelled."
            }, status=403)

        return Response({
            "success": False,
            "message": f"Invalid OTP. Attempts remaining: {remaining}"
        }, status=403)

    # 🟢 7️⃣ OTP CORRECT — FINALIZE WITHDRAWAL (ATOMIC)
    with db_transaction.atomic():

        # Lock account row
        account = txn.account
        account.refresh_from_db()

        # Safety check
        if account.balance < txn.amount:
            txn.status = Transaction.STATUS_CANCELLED
            txn.save(update_fields=["status"])
            return Response({
                "success": False,
                "message": "Insufficient balance"
            }, status=400)

        # Deduct money
        account.balance -= txn.amount
        account.save(update_fields=["balance"])

        # Mark OTP used
        challenge.is_used = True
        challenge.save(update_fields=["is_used"])

        # Complete transaction
        txn.status = Transaction.STATUS_COMPLETED
        txn.save(update_fields=["status"])

    # 8️⃣ Send success SMS
    send_sms(
        account.phone_number,
        f"₹{txn.amount} withdrawn successfully.\nAvailable Balance: ₹{account.balance}"
    )

    return Response({
        "success": True,
        "message": "OTP verified. Withdrawal successful.",
        "data": {
            "withdrawn": txn.amount,
            "balance": account.balance
        }
    })
def is_account_blocked(account):
    """Check if account is blocked and auto-unblock if time passed."""
    if account.is_blocked:
        if account.blocked_until and timezone.now() < account.blocked_until:
            return True
        else:
            account.is_blocked = False
            # account.failed_attempts = 0
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
        account = Account.objects.get(account_id=int(account_id))

        # 🔒 If already blocked
        if account.is_blocked:
            if account.blocked_until and timezone.now() < account.blocked_until:
                return "BLOCKED"
            else:
                account.is_blocked = False
                account.failed_attempts = 0
                account.blocked_until = None
                account.save()

        # ❌ Wrong PIN
        if not account.verify_pin(pin):

            account.failed_attempts += 1

            if account.failed_attempts >= 3:
                account.block_count += 1

                # 🚫 Permanent block
                if account.block_count >= 3:
                    account.is_permanent_block = True
                    account.is_blocked = True

                    account.failed_attempts = 0
                    account.save()
                    return "PERMANENT_BLOCK"

                # ⏳ Temporary block
                if account.block_count == 1:
                    block_minutes = 5
                elif account.block_count == 2:
                    block_minutes = 10

                account.is_blocked = True
                account.blocked_until = timezone.now() + timedelta(minutes=block_minutes)
                account.failed_attempts = 0
                account.save()

                return "BLOCKED"

            account.save()
            return None

        # ✅ Correct PIN
        account.failed_attempts = 0
        account.block_count = 0
        account.is_blocked = False
        account.blocked_until = None
        account.save()

        return account

    except Account.DoesNotExist:
        return None


# def get_today_withdraw_total(account):
#     today = timezone.now().date()
#     return sum(tx.amount for tx in Transaction.objects.filter(account=account, transaction_type="WITHDRAW", timestamp__date=today))

# def get_today_withdraw_count(account):
#     today = timezone.now().date()
#     return Transaction.objects.filter(account=account, transaction_type="WITHDRAW", timestamp__date=today).count()

# def get_today_deposit_total(account):
#     today = timezone.now().date()
#     return sum(tx.amount for tx in Transaction.objects.filter(account=account, transaction_type="DEPOSIT", timestamp__date=today))

# ---------------- QR Login ----------------
@api_view(['POST'])
def qr_login(request):
    file = request.FILES.get("qr")
    if not file:
        return Response({"success": False, "message": "File not found"}, status=404)

    try:
        img = Image.open(file)
    except:
        return Response({"success": False, "message": "Invalid QR"}, status=400)

    decoded = decode(img)
    if not decoded:
        return Response({"success": False, "message": "QR code is invalid or unreadable"}, status=400)

    token = decoded[0].data.decode("utf-8")
    account = Account.objects.filter(qr_token=token).first()
    if not account:
         return Response({"success": False, "message": "Account not found for this QR"}, status=404)
    if account.is_permanent_block:
        return Response({
            "success": False,
            "is_permanent_block": True
        })
    if account.is_blocked:
        if account.blocked_until and timezone.now() < account.blocked_until:
            remaining_seconds = int(
                (account.blocked_until - timezone.now()).total_seconds()
            )

            return Response({
                "success": False,
                "is_blocked": True,
                "remaining_seconds": remaining_seconds
            })

    # Login successful
    return Response({
        "success": True,
        "message": "QR login successful",
        "data": {"account_id": account.account_id, "holder_name": account.holder_name}
    })

# ---------------- Operation APIs (PIN per action) ----------------

@api_view(['POST'])
def deposit(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')
    amount = request.data.get('amount')

    if not all([account_id, pin, amount]):
        return Response(
            {"success": False, "message": "account_id, pin and amount are required"},
            status=400
        )

    account = get_account_with_pin(account_id, pin)

    # ❌ If account invalid or blocked
    if not account:
        acc = Account.objects.filter(account_id=account_id).first()

        if acc and acc.is_blocked:
            return Response(
                {"success": False, "message": "Account temporarily blocked"},
                status=403
            )

        return Response(
            {"success": False, "message": "Invalid PIN"},
            status=403
        )

    # ✅ Now continue normally (ONLY if account is valid)

    try:
        amount = Decimal(amount)
        if amount <= 0:
            return Response(
                {"success": False, "message": "Amount must be greater than 0"},
                status=400
            )
    except:
        return Response(
            {"success": False, "message": "Invalid amount"},
            status=400
        )

    # if get_today_deposit_total(account) + amount > 50000:
    #     return Response(
    #         {"success": False, "message": "Daily deposit limit exceeded (50000)"},
    #         status=400
    #     )

    account.deposit(amount)

    Transaction.objects.create(
        account=account,
        transaction_type='DEPOSIT',
        amount=amount,
        remark='ATM Deposit'
    )
    # send_sms(
    # account.phone_number,
    # f"₹{amount} deposited successfully.\nAvailable Balance: ₹{account.balance}")

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

    # 1️⃣ Account + PIN validation
    account = get_account_with_pin(account_id, pin)
    if not account:
        return Response({"success": False, "message": "Invalid PIN"}, status=403)

    if is_account_blocked(account):
        return Response({"success": False, "message": "Account temporarily blocked"}, status=403)

    # 2️⃣ Amount validation
    try:
        amount = Decimal(amount)
    except:
        return Response({"success": False, "message": "Invalid amount"}, status=400)

    if amount <= 0:
        return Response({"success": False, "message": "Amount must be greater than zero"}, status=400)

    # 3️⃣ Limits (unchanged)
    # if get_today_withdraw_count(account) >= 10:
    #     return Response({"success": False, "message": "Maximum 5 withdrawals per day allowed"}, status=400)

    # if get_today_withdraw_total(account) + amount > 40000:
    #     return Response({"success": False, "message": "Daily withdrawal limit reached (40000)"}, status=400)

    # 4️⃣ AI fraud detection (unchanged)
    # if check_transaction(account, amount):
    #     return Response({
    #         "success": False,
    #         "message": "Suspicious activity detected. Transaction blocked."
    #     }, status=403)

    # 🔀 5️⃣ DECISION POINT (this is the core change)

    # 🟢 SMALL AMOUNT → INSTANT WITHDRAW
    if amount <= OTP_THRESHOLD:

        if not account.withdraw(amount):
            return Response({"success": False, "message": "Insufficient balance"}, status=400)

        Transaction.objects.create(
            account=account,
            transaction_type='WITHDRAW',
            amount=amount,
            remark='ATM Withdraw',
            status=Transaction.STATUS_COMPLETED
        )

        # send_sms(
        #     account.phone_number,
        #     f"₹{amount} withdrawn successfully.\nAvailable Balance: ₹{account.balance}"
        # )

        return Response({
            "success": True,
            "otp_required": False,
            "message": "Withdrawal successful",
            "data": {
                "withdrawn": amount,
                "balance": account.balance
            }
        })

    # 🟠 LARGE AMOUNT → OTP REQUIRED (NO MONEY MOVES HERE)

    # 6️⃣ Create pending transaction
    txn = Transaction.objects.create(
        account=account,
        transaction_type='WITHDRAW',
        amount=amount,
        remark='ATM Withdraw (OTP Required)',
        status=Transaction.STATUS_PENDING_OTP
    )

    # 7️⃣ Generate & store OTP
    otp = generate_otp()

    OtpChallenge.objects.create(
        account=account,
        transaction=txn,
        otp_hash=hash_otp(otp),
        expires_at=otp_expiry(minutes=1)
    )

    # 8️⃣ Send OTP SMS (NOT success SMS)
    send_sms(
        account.phone_number,
        f"OTP for withdrawing ₹{amount} is {otp}. Valid for 1 minutes."
    )

    # 9️⃣ Respond to frontend
    return Response({
        "success": True,
        "otp_required": True,
        "transaction_id": txn.id,
        "message": "OTP sent to registered mobile number"
    })
# @api_view(['POST'])
# def balance_inquiry(request):
#     account_id = request.data.get('account_id')
#     pin = request.data.get('pin')
   
#     print(pin)
   
#     account = get_account_with_pin(account_id, pin)
#     print("account",account)
  
#     if not account:
#         return Response({"success": False, "message": "Invalid PIN"}, status=403)

#     if is_account_blocked(account):
#         return Response({"success": False, "message": "Account temporarily blocked","blocking_status":account.is_blocked },status=403)

    
#     return Response({
#         "success": True,
#         "message": "Balance fetched successfully, session ended",
#         "data": {"balance": account.balance, "holder_name": account.holder_name,"blocking_status":account.is_blocked}
#     })


@api_view(['POST'])
def balance_inquiry(request):
    account_id = request.data.get('account_id')
    pin = request.data.get('pin')

    account = get_account_with_pin(account_id, pin)
    print(account)

    # 🔒 If Blocked
    if account == "PERMANENT_BLOCK":
     return Response({
        "success": False,
        "is_permanent_block": True,
        "message": "Account permanently blocked. Contact the bank."
     }, status=403)
     
    if account == "BLOCKED":
       acc = Account.objects.get(account_id=account_id)

       remaining_seconds = int(
        (acc.blocked_until - timezone.now()).total_seconds()
       )

       return Response({
            "success": False,
            "is_blocked": True,
            "remaining_seconds": remaining_seconds,
            "message": "Account temporarily blocked."
        }, status=403)
    
    if not account:
        return Response({
        "success": False,
        "message": "Invalid PIN"
            }, status=403)

    return Response({
        "success": True,
        "balance": account.balance
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
    new_pin = request.data.get('new_pin')
    confirm_pin = request.data.get('confirm_pin')

    if not all([account_id, new_pin, confirm_pin]):
        return Response(
            {"success": False, "message": "All fields are required"},
            status=400
        )

    # Validate PIN format
    if not new_pin.isdigit() or len(new_pin) != 4:
        return Response(
            {"success": False, "message": "PIN must be a 4-digit number"},
            status=400
        )

    # Confirm PIN match
    if new_pin != confirm_pin:
        return Response(
            {"success": False, "message": "PINs do not match"},
            status=400
        )

    try:
        account = Account.objects.get(account_id=account_id)
    except Account.DoesNotExist:
        return Response(
            {"success": False, "message": "Account not found"},
            status=404
        )

    # Optional: Prevent same PIN reuse
    if account.pin == new_pin:
        return Response(
            {"success": False, "message": "New PIN must be different from old PIN"},
            status=400
        )

    # Update PIN
    account.set_pin(new_pin)  # make sure this method saves

    return Response({
        "success": True,
        "message": "PIN changed successfully. Please login again."
    })

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
        to_account = Account.objects.get(account_id=to_account_id)
    except Account.DoesNotExist:
        return Response({"success": False, "message": "Target account not found"}, status=404)

    if from_account.balance < Decimal(amount):
        return Response({"success": False, "message": "Insufficient funds"}, status=400)

    from_account.balance -= Decimal(amount)
    to_account.balance += Decimal(amount)
    from_account.save()
    to_account.save()
    # send_sms(
    # from_account.phone_number,
    # f"₹{amount} transferred.\nAvailable Balance: ₹{from_account.balance}"
# )

    # Session ends after action
    return Response({"success": True, "message": "Transfer successful, session ended"})