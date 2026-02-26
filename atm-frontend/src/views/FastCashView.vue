<template>
  <div class="transaction-view">
    <h2>Fast Cash</h2>

    <!-- Fast Cash Buttons -->
    <div class="fast-buttons">
      <button v-for="amt in amounts" :key="amt" @click="submitFastCash(amt)">
        ₹{{ amt }}
      </button>
    </div>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { fastCash } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      amounts: [100, 200, 500, 1000, 2000, 5000],
      message: "",
    };
  },
  methods: {
    async submitFastCash(amount) {
      try {
        const data = await fastCash({
          account_id: this.accountId,
          pin: this.pin,
          amount,
        });

        this.message = data.message;

        if (data.success) {
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

.fast-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
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
