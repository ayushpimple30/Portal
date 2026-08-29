document.querySelectorAll('.notice-close').forEach((button) => button.addEventListener('click', () => button.closest('.toast-notice').remove()));
const password = document.querySelector('[name="password"]');
const indicator = document.querySelector('[data-password-strength]');
if (password && indicator) password.addEventListener('input', () => { const score = [password.value.length >= 8, /[A-Z]/.test(password.value), /[0-9]/.test(password.value), /[^A-Za-z0-9]/.test(password.value)].filter(Boolean).length; indicator.dataset.level = score; indicator.textContent = ['', 'Weak password', 'Fair password', 'Good password', 'Strong password'][score]; });
