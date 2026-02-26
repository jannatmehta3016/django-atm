<template>
  <div class="transaction-view">
    <h2>Deposit</h2>
    <input type="number" v-model="amount" placeholder="Enter Amount" />
    <button @click="submitDeposit">Deposit</button>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import { deposit } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      amount: 0,
      message: "",
    };
  },
  methods: {
    async submitDeposit() {
      if (this.amount <= 0) {
        this.message = "Enter valid amount";
        return;
      }
      try {
        const res = await deposit({
          account_id: this.accountId,
          pin: this.pin,
          amount: this.amount,
        });
        this.message = res.message;
        if (res.success) setTimeout(() => this.$emit("logout"), 2000);
      } catch {
        this.message = "Server error";
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
