const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  transpileDependencies: true,

  devServer: {
    host: "0.0.0.0",
    port: 8080,
    allowedHosts: "all",

    proxy: {
      "/api": {
        target: "http://192.168.1.52:8000",
        changeOrigin: true,
      },
    },
  },
});
