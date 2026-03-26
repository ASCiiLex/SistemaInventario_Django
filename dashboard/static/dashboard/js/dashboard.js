/* ============================================
   INICIALIZACIÓN DE SECCIONES
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
            content.style.display = isClosed ? "none" : "block";
            arrow.classList.toggle("arrow-up", !isClosed);
            arrow.classList.toggle("arrow-down", isClosed);
        };
    });
}

function initSubSections() {
    document.querySelectorAll(".subsection").forEach(sub => {
        const header = sub.querySelector(".subsection-header");
        const content = sub.querySelector(".subsection-content");
        const arrow = sub.querySelector(".sub-toggle-arrow");

        if (!header || !content || !arrow) return;

        sub.classList.add("closed");
        content.style.display = "none";

        header.onclick = () => {
            const isClosed = sub.classList.toggle("closed");
            content.style.display = isClosed ? "none" : "block";
            arrow.classList.toggle("sub-arrow-up", !isClosed);
            arrow.classList.toggle("sub-arrow-down", isClosed);
        };
    });
}

/* ============================================
   CHART (CORRECTO)
============================================ */

let categoryChart = null;

function initChart() {
    const canvas = document.getElementById("categoryChart");
    if (!canvas) return;

    if (!window.chartData) return;

    const labels = window.chartData.labels || [];
    const values = window.chartData.values || [];

    if (!labels.length) return;

    if (categoryChart) {
        categoryChart.destroy();
    }

    categoryChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Stock",
                data: values,
                backgroundColor: "#0d6efd"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: "y",
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

    selector.onchange = function () {
        fetch(`/dashboard/grafico/${this.value}/`)
            .then(r => r.json())
            .then(data => {
                categoryChart.data.labels = data.labels || [];
                categoryChart.data.datasets[0].data = data.values || [];
                categoryChart.update();
            });
    };
}

/* ============================================
   EVENTS
============================================ */

document.addEventListener("DOMContentLoaded", () => {
    initMainSections();
    initSubSections();
    initChart();
});

document.body.addEventListener("htmx:afterSwap", () => {
    initMainSections();
    initSubSections();
    initChart();
});