# from django.contrib import admin
# from .models import Account,Transaction

# admin.site.register(Account)
# admin.site.register(Transaction)
from django.contrib import admin
from .models import Account, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "holder_name", "balance", "account_type")
    search_fields = ("account_number", "holder_name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "transaction_type", "amount", "timestamp")
    list_filter = ("transaction_type", "timestamp","is_fraud")
    readonly_fields = ("timestamp",)

