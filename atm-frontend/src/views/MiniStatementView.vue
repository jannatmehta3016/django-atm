<template>
  <div class="transaction-view">
    <h2>Mini Statement</h2>
    <button @click="getMiniStatement">Get Statement</button>

    <p v-if="message" class="message">{{ message }}</p>

    <ul v-if="transactions.length">
      <li v-for="tx in transactions" :key="tx.timestamp">
        {{ tx.timestamp }} | {{ tx.type }} | ₹{{ tx.amount }} | {{ tx.remark }}
      </li>
    </ul>
  </div>
</template>

<script>
import { miniStatement } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      transactions: [],
      message: "",
    };
  },
  methods: {
    async getMiniStatement() {
      try {
        const data = await miniStatement({
          account_id: this.accountId,
          pin: this.pin,
        });

        this.message = data.message;

        if (data.success) {
          this.transactions = data.data.transactions;
          setTimeout(() => {
            this.$emit("logout");
          }, 2000);
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
  margin-top: 15px;
}

.message {
  margin-top: 15px;
  font-weight: bold;
  color: yellow;
}

ul {
  margin-top: 15px;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

li {
  margin-bottom: 5px;
}
</style>
