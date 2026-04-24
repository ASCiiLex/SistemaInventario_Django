export function initMainSections() {
    document.querySelectorAll(".card-section").forEach(section => {
        const header = section.querySelector(".section-header");
        const content = section.querySelector(".section-content");
        const arrow = section.querySelector(".toggle-arrow");

        if (!header || !content || !arrow) return;

        if (section.dataset.bound === "true") return;
        section.dataset.bound = "true";

        // 🔥 SIEMPRE ABIERTO POR DEFECTO
        section.classList.remove("closed");
        content.style.display = "block";
        arrow.classList.add("arrow-up");
        arrow.classList.remove("arrow-down");

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

        if (sub.dataset.bound === "true") return;
        sub.dataset.bound = "true";

        // 🔥 SIEMPRE CERRADO POR DEFECTO
        sub.classList.add("closed");
        content.style.display = "none";
        arrow.classList.add("sub-arrow-down");
        arrow.classList.remove("sub-arrow-up");

        header.addEventListener("click", () => {
            const nowClosed = sub.classList.toggle("closed");

            content.style.display = nowClosed ? "none" : "block";
            arrow.classList.toggle("sub-arrow-up", !nowClosed);
            arrow.classList.toggle("sub-arrow-down", nowClosed);
        });
    });
}