function toggleForm() {
  const form = document.getElementById('addForm');
  if (!form) return;
  const isHidden = form.style.display === 'none' || form.style.display === '';
  form.style.display = isHidden ? 'block' : 'none';
  if (isHidden) {
    form.querySelector('input[type="number"]')?.focus();
  }
}

// Set today's date as default on date inputs
document.addEventListener('DOMContentLoaded', () => {
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const today = new Date().toISOString().split('T')[0];
  dateInputs.forEach(input => {
    if (!input.value) input.value = today;
  });

  // Auto-dismiss alerts
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    });
  }, 3000);
});
