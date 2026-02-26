<template>
  <div class="transaction-view">
    <h2>Transfer Money</h2>

    <input
      type="number"
      v-model="toAccountId"
      placeholder="Enter Target Account ID"
    />
    <input type="number" v-model="amount" placeholder="Enter Amount" />

    <button @click="submitTransfer">Transfer</button>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { transferMoney } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      toAccountId: "",
      amount: 0,
      message: "",
    };
  },
  methods: {
    async submitTransfer() {
      if (!this.toAccountId || this.amount <= 0) {
        this.message = "Enter valid account and amount";
        return;
      }

      try {
        const data = await transferMoney({
          from_account_id: this.accountId,
          to_account_id: this.toAccountId,
          pin: this.pin,
          amount: this.amount,
        });

        this.message = data.message;

        if (data.success) {
          this.toAccountId = "";
          this.amount = 0;
          setTimeout(() => this.$emit("logout"), 2000);
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

input {
  display: block;
  padding: 10px;
  margin: 10px auto;
  width: 200px;
  border-radius: 10px;
  border: 1px solid #ccc;
}

button {
  padding: 10px 20px;
  background: #00c6d7;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 10px;
}

.message {
  margin-top: 15px;
  font-weight: bold;
  color: yellow;
}
</style>
