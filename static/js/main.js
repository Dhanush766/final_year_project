/* Small JavaScript helpers for the Employee Management System.
   Server-side validation in Django is the real protection; this file only
   improves the user experience. */
document.addEventListener("DOMContentLoaded", function () {
  // 1. Automatically hide success/info messages after 6 seconds.
  //    Error and warning messages stay until the user closes them.
  document.querySelectorAll(".alert-success, .alert-info").forEach(function (alertBox) {
    setTimeout(function () {
      if (window.bootstrap && document.body.contains(alertBox)) {
        window.bootstrap.Alert.getOrCreateInstance(alertBox).close();
      }
    }, 6000);
  });

  // 2. Client-side form validation feedback (Bootstrap "was-validated" style).
  document.querySelectorAll("form.needs-validation").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    });
  });

  // 3. Prevent double submission: disable submit buttons after the first click.
  document.querySelectorAll("form[data-single-submit]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (event.defaultPrevented) {
        return; // validation failed, let the user fix the form
      }
      form.querySelectorAll("button[type=submit]").forEach(function (button) {
        button.disabled = true;
      });
    });
  });

  // 4. Employee list: apply the department/status filters as soon as they change.
  document.querySelectorAll("form[data-autosubmit-form]").forEach(function (form) {
    form.querySelectorAll("select").forEach(function (select) {
      select.addEventListener("change", function () {
        form.submit();
      });
    });
  });
});
