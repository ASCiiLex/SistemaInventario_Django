document.addEventListener("DOMContentLoaded", () => {
    const html = document.documentElement;
    const btn = document.getElementById("themeToggle");

    if (!btn) return;

    const saved = localStorage.getItem("theme") || "light";
    html.setAttribute("data-theme", saved);

    updateIcon(saved);

    btn.addEventListener("click", () => {
        const current = html.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";

        html.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);

        updateIcon(next);
    });

    function updateIcon(theme) {
        btn.textContent = theme === "dark" ? "☀️" : "🌙";
    }
});