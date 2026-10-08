const form = document.querySelector("#registerForm");
const passwordInput = document.querySelector("#password");
const strengthText = document.querySelector("#strengthText");
const strengthBars = [...document.querySelectorAll(".strength-meter span")];

const validators = {
  name: (value) => value.trim() ? "" : "请输入你的姓名",
  username: (value) => {
    if (!value.trim()) return "请输入用户名";
    return /^[a-zA-Z0-9_]{3,18}$/.test(value) ? "" : "用户名需为 3-18 位字母、数字或下划线";
  },
  email: (value) => {
    if (!value.trim()) return "请输入邮箱地址";
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? "" : "请输入有效的邮箱地址";
  },
  password: (value) => {
    if (!value) return "请设置密码";
    return value.length >= 8 ? "" : "密码至少需要 8 个字符";
  },
  confirmPassword: (value) => {
    if (!value) return "请再次输入密码";
    return value === passwordInput.value ? "" : "两次输入的密码不一致";
  },
};

function setError(fieldName, message) {
  const input = document.querySelector(`#${fieldName}`);
  const error = document.querySelector(`#${fieldName}Error`);
  input?.classList.toggle("invalid", Boolean(message));
  if (error) error.textContent = message;
  return !message;
}

function validateField(fieldName) {
  const input = document.querySelector(`#${fieldName}`);
  return setError(fieldName, validators[fieldName](input.value));
}

function updatePasswordStrength(value) {
  let score = 0;
  if (value.length >= 8) score += 1;
  if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score += 1;
  if (/\d/.test(value)) score += 1;
  if (/[^A-Za-z0-9]/.test(value)) score += 1;

  const labels = ["未设置", "较弱", "一般", "较强", "很强"];
  const colors = ["#e7e9ef", "#ff9c79", "#f2c14e", "#81b39e", "#4a9e72"];
  strengthBars.forEach((bar, index) => {
    bar.style.background = index < score ? colors[score] : colors[0];
  });
  strengthText.textContent = `密码强度：${labels[score]}`;
}

passwordInput.addEventListener("input", () => {
  updatePasswordStrength(passwordInput.value);
  if (passwordInput.value) validateField("password");
  if (document.querySelector("#confirmPassword").value) validateField("confirmPassword");
});

Object.keys(validators).forEach((fieldName) => {
  document.querySelector(`#${fieldName}`).addEventListener("blur", () => validateField(fieldName));
});

document.querySelectorAll(".toggle-password").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.querySelector(`#${button.dataset.target}`);
    const isHidden = input.type === "password";
    input.type = isHidden ? "text" : "password";
    button.textContent = isHidden ? "隐藏" : "显示";
    button.setAttribute("aria-label", isHidden ? "隐藏密码" : "显示密码");
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const fieldsValid = Object.keys(validators).every(validateField);
  const terms = document.querySelector("#terms");
  const termsError = document.querySelector("#termsError");
  termsError.textContent = terms.checked ? "" : "请先同意服务条款和隐私政策";
  if (!fieldsValid || !terms.checked) return;

  document.querySelector("#successMessage").textContent = "注册信息已通过校验，欢迎加入 Aurora！";
  form.reset();
  updatePasswordStrength("");
});

document.querySelector("#loginLink").addEventListener("click", (event) => {
  event.preventDefault();
  document.querySelector("#successMessage").textContent = "登录功能将在后续课程中实现。";
});
