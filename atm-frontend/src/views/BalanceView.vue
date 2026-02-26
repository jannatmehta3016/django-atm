<template>
  <div class="transaction-view">
    <h2>Balance Inquiry</h2>
    <button @click="getBalance">Check Balance</button>

    <!-- Display message from server -->
    <p v-if="message" class="message">{{ message }}</p>

    <!-- Show balance if fetched -->
    <p v-if="balance !== null" class="balance">Balance: ₹{{ balance }}</p>
  </div>
</template>

<script>
import { balanceInquiry } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      balance: null,
      message: "",
    };
  },
  methods: {
    async getBalance() {
      try {
        // Call API
        const data = await balanceInquiry({
          account_id: this.accountId,
          pin: this.pin,
        });

        // Display backend message
        this.message = data.message;

        // If success, show balance
        if (data.success) {
          this.balance = data.data.balance;
        }
      } catch (err) {
        console.error(err);
        this.message = err.response?.data?.message || "Server error";
      }
    },
  },
};
</script>

<style scoped>
.transaction-view {
  text-align: center;
  margin-top: 50px;
}

button {
  padding: 10px 20px;
  background: #00c6d7;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 20px;
}

.message {
  margin-top: 15px;
  font-weight: bold;
  color: yellow;
}

.balance {
  margin-top: 10px;
  font-weight: bold;
  color: lime;
}
</style>
