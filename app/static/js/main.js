// Auto-dismiss alerts after 4 seconds
document.querySelectorAll(".alert").forEach(el => {
    setTimeout(() => el.classList.remove("show"), 4000);
});
