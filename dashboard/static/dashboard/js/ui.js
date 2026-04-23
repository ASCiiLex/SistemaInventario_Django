export function initMainSections() {
    document.querySelectorAll(".card-section").forEach(section => {
        const header = section.querySelector(".section-header");
        const content = section.querySelector(".section-content");
        const arrow = section.querySelector(".toggle-arrow");

        if (!header || !content || !arrow) return;

        // ✅ evitar re-bind
        if (section.dataset.bound === "true") return;
        section.dataset.bound = "true";

        // ✅ estado inicial SOLO si no existe
        const isClosed = section.classList.contains("closed");

        content.style.display = isClosed ? "none" : "block";
        arrow.classList.toggle("arrow-up", !isClosed);
        arrow.classList.toggle("arrow-down", isClosed);

        header.addEventListener("click", () => {
            const nowClosed = section.classList.toggle("closed");

            content.style.display = nowClosed ? "none" : "block";
            arrow.classList.toggle("arrow-up", !nowClosed);
            arrow.classList.toggle("arrow-down", nowClosed);
        });
    });
}

export function initSubSections() {
    document.querySelectorAll(".subsection").forEach(sub => {
        const header = sub.querySelector(".subsection-header");
        const content = sub.querySelector(".subsection-content");
        const arrow = sub.querySelector(".sub-toggle-arrow");

        if (!header || !content || !arrow) return;

        // ✅ evitar re-bind
        if (sub.dataset.bound === "true") return;
        sub.dataset.bound = "true";

        // ✅ estado inicial SOLO si no existe
        const isClosed = sub.classList.contains("closed");

        content.style.display = isClosed ? "none" : "block";
        arrow.classList.toggle("sub-arrow-up", !isClosed);
        arrow.classList.toggle("sub-arrow-down", isClosed);

        header.addEventListener("click", () => {
            const nowClosed = sub.classList.toggle("closed");

            content.style.display = nowClosed ? "none" : "block";
            arrow.classList.toggle("sub-arrow-up", !nowClosed);
            arrow.classList.toggle("sub-arrow-down", nowClosed);
        });
    });
}