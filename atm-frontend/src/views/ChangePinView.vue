<template>
  <div class="transaction-view">
    <h2>Change PIN</h2>

    <input
      type="password"
      v-model="newPin"
      placeholder="Enter New PIN (4 digits)"
      autocomplete="new-password"
      name="new_pin_12345"
    />

    <input
      type="password"
      v-model="confirmPin"
      placeholder="Confirm New PIN"
      autocomplete="off"
    />

    <button @click="submitChangePin">Change PIN</button>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { changePin } from "@/services/api";
export default {
  props: ["accountId"], // REMOVE pin prop

  data() {
    return {
      newPin: "",
      confirmPin: "",
      message: "",
    };
  },

  methods: {
    async submitChangePin() {
      if (!this.newPin || !this.confirmPin) {
        this.message = "All fields are required";
        return;
      }

      if (this.newPin.length !== 4 || !/^\d+$/.test(this.newPin)) {
        this.message = "PIN must be a 4-digit number";
        return;
      }

      if (this.newPin !== this.confirmPin) {
        this.message = "PINs do not match";
        return;
      }

      try {
        const data = await changePin({
          account_id: this.accountId,
          new_pin: this.newPin,
          confirm_pin: this.confirmPin,
        });

        this.message = data.message;

        if (data.success) {
          this.newPin = "";
          this.confirmPin = "";

          setTimeout(() => this.$emit("logout"), 2000);
        }
      } catch (err) {
        this.message = err.response?.data?.message || "Server error";
      }
    },
  },
};
// export default {
//   props: ["accountId", "pin"],
//   data() {
//     return {
//       oldPin: "",
//       newPin: "",
//       message: "",
//     };
//   },
//   methods: {
//     async submitChangePin() {
//       if (!this.oldPin || !this.newPin) {
//         this.message = "All fields are required";
//         return;
//       }

//       if (this.newPin.length !== 4 || !/^\d+$/.test(this.newPin)) {
//         this.message = "New PIN must be a 4-digit number";
//         return;
//       }

//       try {
//         const data = await changePin({
//           account_id: this.accountId,
//           old_pin: this.oldPin,
//           new_pin: this.newPin,
//         });

//         this.message = data.message;

//         if (data.success) {
//           this.oldPin = "";
//           this.newPin = "";
//           setTimeout(() => this.$emit("logout"), 2000);
//         }
//       } catch (err) {
//         console.error(err);
//         this.message = err.response?.data?.message || "Server error";
//       }
//     },
//   },
// };
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
