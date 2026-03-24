document.addEventListener("DOMContentLoaded", () => {

    /* ============================
       SECCIONES PRINCIPALES
    ============================ */
    document.querySelectorAll(".card-section").forEach(section => {

        const header = section.querySelector(".section-header");
        const content = section.querySelector(".section-content");
        const arrow = section.querySelector(".toggle-arrow");

        header.addEventListener("click", () => {
            const isClosed = section.classList.toggle("closed");
            arrow.textContent = isClosed ? "▲" : "▼";
            content.style.display = isClosed ? "none" : "block";
        });
    });

    /* ============================
       SUBSECCIONES INTERNAS
    ============================ */
    document.querySelectorAll(".subsection").forEach(sub => {

        const header = sub.querySelector(".subsection-header");
        const content = sub.querySelector(".subsection-content");
        const arrow = sub.querySelector(".sub-toggle-arrow");

        header.addEventListener("click", () => {
            const isClosed = sub.classList.toggle("closed");
            arrow.textContent = isClosed ? "▸" : "▾";
            content.style.display = isClosed ? "none" : "block";
        });
    });

    /* ============================
       GRÁFICO HORIZONTAL
    ============================ */
    if (window.categoryChartData) {
        const ctx = document.getElementById("categoryChart");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels: window.categoryChartData.labels,
                datasets: [{
                    label: "Stock",
                    data: window.categoryChartData.values,
                    backgroundColor: "#0d6efd"
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                scales: {
                    x: { beginAtZero: true }
                }
            }
        });
    }

});