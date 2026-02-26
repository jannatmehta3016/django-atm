<template>
  <div class="transaction-view">
    <h2>Withdraw</h2>
    <input type="number" v-model="amount" placeholder="Enter Amount" />
    <button @click="submitWithdraw">Withdraw</button>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { withdraw } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      amount: 0,
      message: "",
    };
  },
  methods: {
    async submitWithdraw() {
      if (this.amount <= 0) {
        this.message = "Enter a valid amount";
        return;
      }

      try {
        const data = await withdraw({
          account_id: this.accountId,
          pin: this.pin,
          amount: this.amount,
        });

        this.message = data.message;

        if (data.success) {
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
</style>
