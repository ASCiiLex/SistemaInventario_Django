(function () {
    const STORAGE_KEY = "theme";

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem(STORAGE_KEY, theme);
        updateIcons(theme);
    }

    function updateIcons(theme) {
        document.querySelectorAll("#themeToggle").forEach(btn => {
            btn.textContent = theme === "dark" ? "☀️" : "🌙";
        });
    }

    function initTheme() {
        const saved = localStorage.getItem(STORAGE_KEY) || "light";
        applyTheme(saved);
    }

    function bindEvents() {
        document.addEventListener("click", (e) => {
            const btn = e.target.closest("#themeToggle");
            if (!btn) return;

            const current = document.documentElement.getAttribute("data-theme") || "light";
            const next = current === "dark" ? "light" : "dark";
            applyTheme(next);
        });
    }

    // 🔥 Soporte HTMX + carga inicial
    document.addEventListener("DOMContentLoaded", initTheme);
    document.addEventListener("htmx:load", initTheme);

    bindEvents();
})();