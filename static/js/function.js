const loginModeBtn = document.getElementById('login-mode');
const signupModeBtn = document.getElementById('signup-mode');
const heading = document.getElementById('form-heading');
const text = document.getElementById('form-text');
const confirmGroup = document.getElementById('confirm-group');
const submitButton = document.getElementById('submit-button');
const helperRow = document.getElementById('helper-row');
const modeNote = document.getElementById('mode-note');

function setMode(isSignup) {

  loginModeBtn.classList.toggle('active', !isSignup);
  signupModeBtn.classList.toggle('active', isSignup);

  heading.textContent = isSignup ? 'CREARE CONT' : 'LOGIN';

  text.textContent = isSignup
    ? 'Creează-ți un cont nou și accesează funcționalitățile fără bariere.'
    : 'Introdu datele tale pentru a continua.';

  submitButton.textContent = isSignup
    ? 'CREAZĂ CONT'
    : 'LOGIN';

  confirmGroup.classList.toggle('hidden', !isSignup);

  helperRow.style.display = isSignup
    ? 'none'
    : 'flex';

  modeNote.textContent = isSignup
    ? 'Completează datele pentru a-ți crea un cont nou.'
    : 'Navighează rapid și sigur cu contul tău — design modern, curat și centrat pentru orice ecran.';

  // <<< Asta este modificarea importantă >>>
  document.getElementById("auth-mode").value =
      isSignup ? "register" : "login";
}

loginModeBtn.addEventListener('click', () => setMode(false));
signupModeBtn.addEventListener('click', () => setMode(true));
