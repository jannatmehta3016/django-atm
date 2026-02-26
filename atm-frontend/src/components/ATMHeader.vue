<template>
  <div class="atm-header">
    <img src="@/assets/logo.png" alt="SBI Logo" class="logo" />

    <h3 v-if="userName">Welcome {{ userName }} 👋</h3>
  </div>
</template>

<script>
export default {
  name: "ATMHeader",
  data() {
    return {
      userName: "",
    };
  },
  mounted() {
    this.userName = localStorage.getItem("holder_name");
  },
};
</script>

<style scoped>
.atm-header {
  text-align: center;
  margin-bottom: 20px;
}

.logo {
  width: 110px;
  margin-bottom: 10px;
}
</style>
