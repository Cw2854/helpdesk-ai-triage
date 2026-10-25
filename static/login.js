// Interactive touches for the sign-in page.
// The page still works without JavaScript; these just make it friendlier.

(function () {
  const form = document.querySelector(".signin-form");
  if (!form) return;

  const username = form.querySelector("#username");
  const password = form.querySelector("#password");
  const reveal = form.querySelector(".reveal");
  const capsWarning = document.getElementById("caps-warning");
  const missing = document.getElementById("missing");
  const submit = form.querySelector(".submit");

  // 1. Show / hide the password
  reveal.hidden = false; // only shown when JavaScript is running
  reveal.addEventListener("click", function () {
    const showing = password.type === "text";
    password.type = showing ? "password" : "text";
    reveal.textContent = showing ? "Show" : "Hide";
    reveal.setAttribute("aria-pressed", String(!showing));
    password.focus();
  });

  // 2. Warn when Caps Lock is on (a classic cause of "wrong password" calls)
  function checkCapsLock(event) {
    if (event.getModifierState) {
      capsWarning.hidden = !event.getModifierState("CapsLock");
    }
  }
  password.addEventListener("keydown", checkCapsLock);
  password.addEventListener("keyup", checkCapsLock);
  password.addEventListener("blur", function () { capsWarning.hidden = true; });

  // 3. Check both boxes are filled in, then show that it's working
  form.addEventListener("submit", function (event) {
    if (!username.value.trim() || !password.value) {
      event.preventDefault();
      missing.hidden = false;
      (username.value.trim() ? password : username).focus();
      return;
    }
    missing.hidden = true;
    submit.disabled = true;
    submit.textContent = "Signing in…";
  });

  // 4. Count down a lockout, then let the person try again
  const lockout = document.getElementById("lockout");
  if (lockout) {
    let seconds = parseInt(lockout.dataset.seconds, 10) || 0;
    const clock = lockout.querySelector(".countdown");
    const timer = setInterval(function () {
      seconds -= 1;
      if (seconds <= 0) {
        clearInterval(timer);
        lockout.textContent = "You can try again now.";
        lockout.classList.replace("alert", "notice");
        submit.disabled = false;
        return;
      }
      clock.textContent = Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2, "0");
    }, 1000);
  }
})();
