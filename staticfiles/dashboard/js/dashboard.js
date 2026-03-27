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
   CHART + LOCALSTORAGE
============================================ */

let categoryChart = null;

function getSavedChartType() {
    return localStorage.getItem("dashboardChartType") || "categorias";
}

function saveChartType(tipo) {
    localStorage.setItem("dashboardChartType", tipo);
}

function initChart() {
    const canvas = document.getElementById("categoryChart");
    if (!canvas || !window.chartData) return;

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
            animation: { duration: 500 },
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

    if (selector.dataset.bound === "true") return;
    selector.dataset.bound = "true";

    const savedType = getSavedChartType();
    selector.value = savedType;

    loadChartData(savedType);

    selector.addEventListener("change", function () {
        const tipo = this.value;
        saveChartType(tipo);
        loadChartData(tipo);
    });
}

async function loadChartData(tipo) {
    const loader = document.getElementById("chart-loader");

    try {
        if (loader) loader.style.display = "flex";

        const response = await fetch(
            window.dashboardChartUrl.replace("TIPO", tipo)
        );

        const data = await response.json();

        if (!categoryChart) return;

        categoryChart.data.labels = data.labels || [];
        categoryChart.data.datasets[0].data = data.values || [];

        categoryChart.update();

    } catch (error) {
        console.error("Error cargando gráfico:", error);

    } finally {
        if (loader) loader.style.display = "none";
    }
}

/* ============================================
   REALTIME DASHBOARD
============================================ */

function refreshDashboard() {
    htmx.trigger("#kpis-container", "refresh");
    htmx.trigger("#low-stock-container", "refresh");
    htmx.trigger("#activity-container", "refresh");
}

function initRealtime() {
    document.body.addEventListener("movement-created", () => {
        refreshDashboard();
        refreshChart();
    });

    document.body.addEventListener("notifications-updated", () => {
        refreshDashboard();
    });
}

function refreshChart() {
    const selector = document.getElementById("chartSelector");
    if (!selector) return;

    loadChartData(selector.value);
}

/* ============================================
   EVENTS
============================================ */

function initAll() {
    initMainSections();
    initSubSections();
    initChart();
    initRealtime();
}

document.addEventListener("DOMContentLoaded", initAll);
document.body.addEventListener("htmx:afterSwap", initAll);