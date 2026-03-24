document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".card-section").forEach(section => {

        const header = section.querySelector(".section-header");
        const content = section.querySelector(".section-content");
        const arrow = section.querySelector(".toggle-arrow");

        header.addEventListener("click", () => {

            const isClosed = section.classList.toggle("closed");

            arrow.textContent = isClosed ? "▲" : "▼";

            if (isClosed) {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    });

});