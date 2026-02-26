<template>
  <div class="atm-wrapper">
    <div class="atm-screen">
      <!-- Header -->
      <div class="atm-header">
        <img src="@/assets/sbi.png" alt="SBI Logo" class="logo" />
        <h2 v-if="holderName">Welcome {{ holderName }}</h2>
        <h3 v-if="!currentTransaction">Select Transaction</h3>
      </div>

      <!-- PIN Input -->
      <div v-if="showPinInput" class="pin-verification">
        <p>Enter PIN for {{ selectedTransaction }}:</p>
        <input type="password" v-model="pinAttempt" placeholder="Enter PIN" />
        <div class="pin-buttons">
          <button @click="verifyPin">Submit</button>
          <button @click="cancelPin">Cancel</button>
        </div>
        <p v-if="pinError" class="error">{{ pinError }}</p>
      </div>

      <!-- Transaction Component -->
      <component
        v-else-if="currentTransaction"
        :is="currentTransaction"
        :account-id="accountId"
        :pin="verifiedPin"
        @logout="logout"
      />

      <!-- Menu Buttons -->
      <div v-else class="atm-body">
        <div class="left-buttons">
          <button @click="openPin('Deposit')">Deposit</button>
          <button @click="openPin('Withdraw')">Withdraw</button>
          <button @click="openPin('BalanceInquiry')">Balance</button>
          <button @click="openPin('TransferMoney')">Transfer</button>
        </div>
        <div class="right-buttons">
          <button @click="openPin('FastCash')">Fast Cash</button>
          <button @click="openPin('MiniStatement')">Mini Statement</button>
          <button @click="openPin('ChangePIN')">Change PIN</button>
          <button @click="logout">Exit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Deposit from "./DepositView.vue";
import Withdraw from "./WithdrawView.vue";
import BalanceInquiry from "./BalanceView.vue";
import MiniStatement from "./MiniStatementView.vue";
import FastCash from "./FastCashView.vue";
import ChangePIN from "./ChangePinView.vue";
import TransferMoney from "./TransferView.vue";
import api from "@/services/api";

export default {
  name: "MenuView",
  components: {
    Deposit,
    Withdraw,
    BalanceInquiry,
    MiniStatement,
    FastCash,
    ChangePIN,
    TransferMoney,
  },
  data() {
    return {
      holderName: "",
      accountId: null,
      showPinInput: false,
      pinAttempt: "",
      pinError: "",
      selectedTransaction: null,
      currentTransaction: null,
      verifiedPin: null,
    };
  },
  mounted() {
    this.holderName = localStorage.getItem("holder_name");
    this.accountId = localStorage.getItem("account_id");
  },
  methods: {
    openPin(transaction) {
      this.selectedTransaction = transaction;
      this.showPinInput = true;
      this.pinAttempt = "";
      this.pinError = "";
    },
    async verifyPin() {
      if (!this.pinAttempt) {
        this.pinError = "Enter PIN";
        return;
      }

      try {
        const res = await api.post("balance/", {
          account_id: this.accountId,
          pin: this.pinAttempt,
        });

        const data = res.data; // <-- Axios response data

        if (data.success) {
          this.verifiedPin = this.pinAttempt;
          this.showPinInput = false;

          const componentMap = {
            Deposit,
            Withdraw,
            BalanceInquiry,
            MiniStatement,
            FastCash,
            ChangePIN,
            TransferMoney,
          };
          this.currentTransaction = componentMap[this.selectedTransaction];
        } else {
          this.pinError = data.message || "Invalid PIN";
        }
      } catch (err) {
        console.error(err); // For debugging
        this.pinError =
          err.response?.data?.message || "Server error. Try again.";
      }
    },
    cancelPin() {
      this.showPinInput = false;
      this.pinAttempt = "";
      this.pinError = "";
    },
    logout() {
      localStorage.clear();
      window.location.href = "/"; // redirect to login page
    },
  },
};
</script>

<style scoped>
.atm-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to bottom, #0f3c94, #1b5fd1);
}
.atm-screen {
  width: 900px;
  height: 500px;
  background: linear-gradient(to bottom right, #1b5fd1, #0f3c94);
  border-radius: 15px;
  color: white;
  display: flex;
  flex-direction: column;
}
.atm-header {
  text-align: center;
  padding: 20px;
}
.logo {
  width: 80px;
  margin-bottom: 10px;
}
.atm-body {
  flex: 1;
  display: flex;
  justify-content: space-between;
  padding: 0 80px;
}
.left-buttons,
.right-buttons {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
button {
  width: 220px;
  padding: 14px;
  border-radius: 30px;
  background: #00c6d7;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
}
.pin-verification {
  margin: 20px auto;
  text-align: center;
  background: rgba(0, 0, 0, 0.15);
  padding: 15px;
  border-radius: 10px;
}
.pin-verification input {
  padding: 10px;
  margin-right: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
.pin-verification .error {
  color: red;
  margin-top: 5px;
}
</style>
