document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const target = form.dataset.target;
    if (target) {
      window.location.href = target;
    }
  });
});
