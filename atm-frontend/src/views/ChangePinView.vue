<template>
  <div class="transaction-view">
    <h2>Change PIN</h2>
    <input type="password" v-model="oldPin" placeholder="Enter Old PIN" />
    <input
      type="password"
      v-model="newPin"
      placeholder="Enter New PIN (6 digits)"
    />
    <button @click="submitChangePin">Change PIN</button>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { changePin } from "@/services/api";

export default {
  props: ["accountId", "pin"],
  data() {
    return {
      oldPin: "",
      newPin: "",
      message: "",
    };
  },
  methods: {
    async submitChangePin() {
      if (!this.oldPin || !this.newPin) {
        this.message = "All fields are required";
        return;
      }

      if (this.newPin.length !== 6 || !/^\d+$/.test(this.newPin)) {
        this.message = "New PIN must be a 6-digit number";
        return;
      }

      try {
        const data = await changePin({
          account_id: this.accountId,
          old_pin: this.oldPin,
          new_pin: this.newPin,
        });

        this.message = data.message;

        if (data.success) {
          this.oldPin = "";
          this.newPin = "";
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
