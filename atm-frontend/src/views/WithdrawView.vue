<template>
  <div class="transaction-view">
    <h2>Withdraw</h2>

    <!-- 🔹 STATE 1: WITHDRAW FORM -->
    <div v-if="!otpRequired && balance === null">
      <input
        type="number"
        v-model.number="amount"
        @focus="clearZero"
        @blur="resetIfEmpty"
        placeholder="Enter Amount"
      />
      <button @click="submitWithdraw" :disabled="loading">Withdraw</button>
    </div>

    <!-- 🔹 STATE 2: OTP VERIFICATION -->
    <div v-if="otpRequired">
      <p class="message">{{ message }}</p>
      <input type="text" v-model="otp" placeholder="Enter OTP" />
      <button @click="submitOtp" :disabled="loading">Verify OTP</button>
    </div>

    <!-- 🔹 STATE 3: SUCCESS -->
    <div v-if="balance !== null">
      <p class="message">{{ message }}</p>
      <p class="balance">Available Balance: ₹{{ balance }}</p>
      <button @click="finishSession">Done</button>
    </div>

    <!-- 🔹 ERROR -->
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import { withdraw, verifyWithdrawOtp } from "@/services/api";

export default {
  props: ["accountId", "pin"],

  data() {
    return {
      // INPUT
      amount: 0,

      // OTP FLOW
      otpRequired: false,
      transactionId: null,
      otp: "",

      // UI
      message: "",
      error: "",
      loading: false,
      balance: null,
    };
  },

  methods: {
    clearZero() {
      if (this.amount === 0) this.amount = "";
    },

    resetIfEmpty() {
      if (this.amount === "") this.amount = 0;
    },

    // 🔹 STEP 1: WITHDRAW REQUEST
    async submitWithdraw() {
      if (this.amount <= 0) {
        this.error = "Enter a valid amount";
        return;
      }

      this.error = "";
      this.message = "";
      this.loading = true;

      try {
        const data = await withdraw({
          account_id: this.accountId,
          pin: this.pin,
          amount: this.amount,
        });

        if (!data.success) {
          this.error = data.message;
          return;
        }

        // 🟢 NO OTP REQUIRED
        if (!data.otp_required) {
          this.message = data.message;
          this.balance = data.data.balance;
          return;
        }

        // 🟠 OTP REQUIRED
        this.otpRequired = true;
        this.transactionId = data.transaction_id;
        this.message = data.message;
      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.message || "Server error";
      } finally {
        this.loading = false;
      }
    },

    // 🔹 STEP 2: OTP VERIFICATION
    async submitOtp() {
      if (!this.otp) {
        this.error = "Please enter OTP";
        return;
      }

      this.error = "";
      this.loading = true;

      try {
        const data = await verifyWithdrawOtp({
          transaction_id: this.transactionId,
          otp: this.otp,
        });

        if (!data.success) {
          this.error = data.message;
          setTimeout(() => {
            this.finishSession();
          }, 2000);

          return;
        }

        // ✅ FINAL SUCCESS
        this.message = data.message;
        this.balance = data.data.balance;
        this.otpRequired = false;
        this.otp = "";
        this.amount = 0;
      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.message || "OTP verification failed";
        setTimeout(() => {
          this.finishSession();
        }, 2000);
      } finally {
        this.loading = false;
      }
    },

    // 🔹 FINISH ATM SESSION
    finishSession() {
      this.$emit("logout");
    },
  },
};
</script>

<style scoped>
.transaction-view {
  text-align: center;
  margin-top: 50px;
}

input {
  padding: 10px;
  margin: 10px 0;
  width: 200px;
}

button {
  padding: 10px 20px;
  background: #00c6d7;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.message {
  margin-top: 15px;
  font-weight: bold;
  color: yellow;
}

.balance {
  margin-top: 10px;
  font-size: 18px;
  color: #00ffcc;
}

.error {
  margin-top: 15px;
  color: red;
  font-weight: bold;
}
</style>
