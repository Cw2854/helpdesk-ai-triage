// Show that the ticket is being sent: the AI triage can take a few seconds.
(function () {
  const form = document.querySelector(".report-form");
  if (!form) return;
  const button = form.querySelector(".submit");
  form.addEventListener("submit", function () {
    button.disabled = true;
    button.textContent = "Sending…";
  });
})();
