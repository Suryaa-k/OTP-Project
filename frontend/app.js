const API_BASE = "http://127.0.0.1:8000";

const mobileInput = document.getElementById("mobile");
const emailInput = document.getElementById("email");
const sendBtn = document.getElementById("sendBtn");
const otpSection = document.getElementById("otpSection");
const mobileOtpInput = document.getElementById("mobileOtp");
const emailOtpInput = document.getElementById("emailOtp");
const verifyBtn = document.getElementById("verifyBtn");
const msg = document.getElementById("msg");

function showMessage(text, type = "error") {
  msg.textContent = text;
  msg.className = type === "success" ? "success" : "error";
}

// Send OTPs
sendBtn.addEventListener("click", async () => {
  const mobile = mobileInput.value.trim();
  const email = emailInput.value.trim();

  if (!mobile || !email) {
    showMessage("Please enter mobile and email.");
    return;
  }

  sendBtn.disabled = true;
  showMessage("Sending OTPs...", "success");

  try {
    const res = await fetch(`${API_BASE}/send-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mobile, email }),
    });

    const data = await res.json();

    if (res.ok && data.success) {
      showMessage("OTPs sent. Check backend console (simulated).", "success");
      otpSection.classList.remove("hidden");
    } else {
      showMessage(data.message || "Failed to send OTPs.");
    }
  } catch (e) {
    showMessage("Server error while sending OTPs.");
  } finally {
    sendBtn.disabled = false;
  }
});

// Verify OTPs
verifyBtn.addEventListener("click", async () => {
  const mobile = mobileInput.value.trim();
  const email = emailInput.value.trim();
  const mobileOtp = mobileOtpInput.value.trim();
  const emailOtp = emailOtpInput.value.trim();

  if (!mobileOtp || !emailOtp) {
    showMessage("Enter both OTPs.");
    return;
  }

  verifyBtn.disabled = true;
  showMessage("Verifying OTPs...", "success");

  try {
    const res = await fetch(`${API_BASE}/verify-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mobile, email, mobileOtp, emailOtp }),
    });

    const data = await res.json();

    if (res.ok && data.verified) {
      showMessage("Both OTPs verified successfully!", "success");
    } else {
      showMessage(data.message || "OTP verification failed.");
    }
  } catch (e) {
    showMessage("Server error while verifying OTPs.");
  } finally {
    verifyBtn.disabled = false;
  }
});
