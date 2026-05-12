// Auto-dismiss Bootstrap alerts after 4 seconds
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert-dismissible").forEach(el => {
    setTimeout(() => {
      if (typeof bootstrap !== "undefined") {
        bootstrap.Alert.getOrCreateInstance(el).close();
      } else {
        el.style.transition = "opacity .4s";
        el.style.opacity = "0";
        setTimeout(() => el.remove(), 400);
      }
    }, 4000);
  });
});
