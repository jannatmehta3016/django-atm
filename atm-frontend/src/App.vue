<template>
  <div id="app">
    <!-- ATM SPA -->
    <ATM />
  </div>
</template>

<script>
import ATM from "./ATM.vue";

export default {
  name: "App",
  components: {
    ATM,
  },
};
</script>

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
}

/* Optional global ATM styles */
.atm-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
