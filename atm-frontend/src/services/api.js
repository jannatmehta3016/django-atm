import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
});

// ----------------- QR Login -----------------
export const qrLogin = async (qrFile) => {
  try {
    const formData = new FormData();
    formData.append("qr", qrFile);

    const res = await api.post("qr-login/", formData);
    return res.data;
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};

// ----------------- Deposit -----------------
export const deposit = async ({ account_id, pin, amount }) => {
  try {
    const res = await api.post("deposit/", { account_id, pin, amount });
    return res.data;
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};
export const withdraw = async ({ account_id, pin, amount }) => {
  try {
    const res = await api.post("withdraw/", { account_id, pin, amount });
    return res.data; // always return res.data
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};
// ----------------- Balance Inquiry -----------------
export const balanceInquiry = async ({ account_id, pin }) => {
  try {
    const res = await api.post("balance/", { account_id, pin });
    return res.data; // always return res.data for consistency
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};
export const fastCash = async ({ account_id, pin, amount }) => {
  try {
    const res = await api.post("fast-cash/", { account_id, pin, amount });
    return res.data; // always return res.data
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};
// ----------------- Mini Statement -----------------
export const miniStatement = async ({ account_id, pin }) => {
  try {
    const res = await api.post("mini-statement/", { account_id, pin });
    return res.data; // always return res.data
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};
// ----------------- Change PIN -----------------
export const changePin = async ({ account_id, old_pin, new_pin }) => {
  try {
    const res = await api.post("change-pin/", { account_id, old_pin, new_pin });
    return res.data; // always return res.data
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};
// ----------------- Transfer Money -----------------
export const transferMoney = async ({
  from_account_id,
  to_account_id,
  pin,
  amount,
}) => {
  try {
    const res = await api.post("transfer/", {
      from_account_id,
      to_account_id,
      pin,
      amount,
    });
    return res.data; // always return res.data
  } catch (err) {
    return {
      success: false,
      message: err.response?.data?.message || "Server error",
    };
  }
};

// ----------------- Verify PIN -----------------
// Uses balance inquiry to verify PIN before allowing transaction
export const verifyPin = async (account_id, pin) => {
  try {
    const res = await api.post("balance/", { account_id, pin });
    if (res.success) return { success: true };
    return { success: false, message: res.message };
  } catch {
    return { success: false, message: "Server error" };
  }
};

export default api;
