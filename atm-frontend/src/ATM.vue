<template>
  <div>
    <!-- Login Screen -->
    <LoginView v-if="currentScreen === 'login'" @login-success="goToMenu" />

    <!-- Menu Screen -->
    <MenuView
      v-if="currentScreen === 'menu'"
      @select-transaction="goToTransaction"
      @logout="logout"
    />

    <!-- Deposit Screen -->
    <DepositView v-if="currentScreen === 'deposit'" @done="goToMenu" />

    <!-- Withdraw Screen -->
    <WithdrawView v-if="currentScreen === 'withdraw'" @done="goToMenu" />

    <!-- Fast Cash Screen -->
    <FastCashView v-if="currentScreen === 'fast-cash'" @done="goToMenu" />

    <!-- Transfer Screen -->
    <TransferView v-if="currentScreen === 'transfer'" @done="goToMenu" />

    <!-- Change PIN Screen -->
    <ChangePinView v-if="currentScreen === 'change-pin'" @done="goToMenu" />

    <!-- Mini Statement Screen -->
    <MiniStatementView
      v-if="currentScreen === 'mini-statement'"
      @done="goToMenu"
    />

    <!-- Balance Inquiry Screen -->
    <BalanceView v-if="currentScreen === 'balance'" @done="goToMenu" />
  </div>
</template>

<script>
// Import all views
import LoginView from "./views/LoginView.vue";
import MenuView from "./views/MenuView.vue";
import DepositView from "./views/DepositView.vue";
import WithdrawView from "./views/WithdrawView.vue";
import FastCashView from "./views/FastCashView.vue";
import TransferView from "./views/TransferView.vue";
import ChangePinView from "./views/ChangePinView.vue";
import MiniStatementView from "./views/MiniStatementView.vue";
import BalanceView from "./views/BalanceView.vue";

export default {
  name: "ATM",
  components: {
    LoginView,
    MenuView,
    DepositView,
    WithdrawView,
    FastCashView,
    TransferView,
    ChangePinView,
    MiniStatementView,
    BalanceView,
  },
  data() {
    return {
      currentScreen: "login", // default screen
    };
  },
  methods: {
    // Go to Menu after successful login
    // goToMenu() {
    //   this.currentScreen = "menu";
    // },
    goToMenu(accountData = null) {
      // Only store data if coming from login
      if (accountData) {
        localStorage.setItem("account_id", accountData.account_id);
        localStorage.setItem("holder_name", accountData.holder_name);
      }

      this.currentScreen = "menu";
    },

    // Go to the selected transaction screen
    goToTransaction(transaction) {
      this.currentScreen = transaction;
    },

    // Logout and return to login screen
    logout() {
      localStorage.clear();
      this.currentScreen = "login";
    },
  },
};
</script>

<style>
/* Global wrapper if needed */
</style>
