from django.urls import path
from . import views

urlpatterns = [
    path("qr-login/", views.qr_login, name="qr_login"),
    path("deposit/", views.deposit, name="deposit"),
    path("withdraw/", views.withdraw, name="withdraw"),
    path("balance/", views.balance_inquiry, name="balance_inquiry"),
    path("mini-statement/", views.mini_statement, name="mini_statement"),
    path("fast-cash/", views.fast_cash, name="fast_cash"),
    path("change-pin/", views.change_pin, name="change_pin"),
    path("transfer/", views.transfer_money, name="transfer_money"),
]