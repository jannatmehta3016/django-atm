<template>
  <div class="atm-wrapper">
    <div class="atm-screen">
      <!-- Header -->
      <div class="atm-header">
        <img src="@/assets/sbi.png" alt="SBI Logo" class="logo" />
        <h2>WELCOME TO SBI ATM</h2>
      </div>

      <!-- QR Upload -->
      <div class="login-section">
        <input type="file" accept="image/*" @change="handleFile" />

        <button @click="uploadQR" :disabled="loading">
          {{ loading ? "Verifying..." : "Upload QR" }}
        </button>

        <p v-if="error" class="message">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "LoginView",

  data() {
    return {
      file: null,
      error: "",
      loading: false,
    };
  },

  methods: {
    handleFile(e) {
      const selected = e.target.files[0];

      if (!selected) return;

      if (!selected.type.startsWith("image/")) {
        this.error = "Please upload an image QR file";
        return;
      }

      this.file = selected;
      this.error = "";
    },

    async uploadQR() {
      this.error = "";
      this.loading = true;

      if (!this.file) {
        this.error = "Select QR file first";
        this.loading = false;
        return;
      }

      const formData = new FormData();
      formData.append("qr", this.file);

      try {
        const res = await api.post("qr-login/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const data = res.data;
        if (data.success) {
          // Save account details to localStorage
          localStorage.setItem("account_id", data.data.account_id);
          localStorage.setItem("holder_name", data.data.holder_name);

          this.$emit("login-success"); // Proceed to ATM main screen
        } else {
          // Show backend error message (Invalid QR, QR not recognized, etc.)
          this.error = data.message || "Invalid QR";
        }
      } catch (err) {
        // Handles backend 400/500 errors
        this.error = err.response?.data?.message || "Invalid QR";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.atm-wrapper {
  height: 100vh;
  background: linear-gradient(to bottom, #0f3c94, #1b5fd1);
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: Arial, sans-serif;
}

.atm-screen {
  width: 400px;
  padding: 30px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

.atm-header {
  text-align: center;
  margin-bottom: 20px;
}

.logo {
  width: 80px;
  margin-bottom: 10px;
}

.login-section {
  display: flex;
  flex-direction: column;
}

.login-section input {
  padding: 10px;
  margin-bottom: 15px;
}

button {
  padding: 10px;
  background-color: #0f3c94;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  margin-top: 10px;
  color: red;
  text-align: center;
}
</style>
