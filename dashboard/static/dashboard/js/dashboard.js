/* ============================================
   INICIALIZACIÓN DE SECCIONES PRINCIPALES
============================================ */

function initMainSections() {
    document.querySelectorAll(".card-section").forEach(section => {
        const header = section.querySelector(".section-header");
        const content = section.querySelector(".section-content");
        const arrow = section.querySelector(".toggle-arrow");

        if (!header || !content || !arrow) return;

        section.classList.remove("closed");
        arrow.classList.remove("arrow-down");
        arrow.classList.add("arrow-up");
        content.style.display = "block";

        header.onclick = () => {
            const isClosed = section.classList.toggle("closed");

            if (isClosed) {
                arrow.classList.remove("arrow-up");
                arrow.classList.add("arrow-down");
                content.style.display = "none";
            } else {
                arrow.classList.remove("arrow-down");
                arrow.classList.add("arrow-up");
                content.style.display = "block";
            }
        };
    });
}

/* ============================================
   INICIALIZACIÓN DE SUBSECCIONES INTERNAS
============================================ */

function initSubSections() {
    document.querySelectorAll(".subsection").forEach(sub => {
        const header = sub.querySelector(".subsection-header");
        const content = sub.querySelector(".subsection-content");
        const arrow = sub.querySelector(".sub-toggle-arrow");

        if (!header || !content || !arrow) return;

        sub.classList.add("closed");
        arrow.classList.remove("sub-arrow-up");
        arrow.classList.add("sub-arrow-down");
        content.style.display = "none";

        header.onclick = () => {
            const isClosed = sub.classList.toggle("closed");

            if (isClosed) {
                arrow.classList.remove("sub-arrow-up");
                arrow.classList.add("sub-arrow-down");
                content.style.display = "none";
            } else {
                arrow.classList.remove("sub-arrow-down");
                arrow.classList.add("sub-arrow-up");
                content.style.display = "block";
            }
        };
    });
}

/* ============================================
   GRÁFICO HORIZONTAL + SELECTOR DINÁMICO
============================================ */

let categoryChart = null;

function initChart() {
    if (!window.categoryChartData) return;

    const ctx = document.getElementById("categoryChart");
    if (!ctx) return;

    categoryChart = new Chart(ctx, {
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

    initChartSelector();
}

function initChartSelector() {
    const selector = document.getElementById("chartSelector");
    if (!selector || !categoryChart) return;

    selector.addEventListener("change", function () {
        const tipo = this.value;

        fetch(`/dashboard/grafico/${tipo}/`)
            .then(response => response.json())
            .then(data => {
                categoryChart.data.labels = data.labels || [];
                categoryChart.data.datasets[0].data = data.values || [];
                categoryChart.update();
            })
            .catch(() => {});
    });
}

/* ============================================
   EVENTOS
============================================ */

document.addEventListener("DOMContentLoaded", () => {
    initMainSections();
    initSubSections();
    initChart();
});

document.body.addEventListener("htmx:afterSwap", () => {
    initMainSections();
    initSubSections();
});
