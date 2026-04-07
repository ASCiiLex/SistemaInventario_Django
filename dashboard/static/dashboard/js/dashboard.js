/* ============================================
   ESTADO GLOBAL
============================================ */

let categoryChart = null;
let realtimeInitialized = false;

/* ============================================
   UI
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
   CHART
============================================ */

function initChart() {
    const canvas = document.getElementById("categoryChart");
    if (!canvas || !window.chartData) return;

    const labels = window.chartData.labels || [];
    const values = window.chartData.values || [];

    if (!labels.length) return;

    if (categoryChart) {
        categoryChart.destroy();
        categoryChart = null;
    }

    categoryChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
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
            animation: { duration: 300 },
            scales: { x: { beginAtZero: true } }
        }
    });

    initChartSelector();
}

function initChartSelector() {
    const selector = document.getElementById("chartSelector");
    if (!selector) return;

    if (selector.dataset.bound === "true") return;
    selector.dataset.bound = "true";

    selector.addEventListener("change", function () {
        loadChartData(this.value);
    });
}

async function loadChartData(tipo) {
    try {
        const response = await fetch(
            window.dashboardChartUrl.replace("TIPO", tipo)
        );

        const data = await response.json();

        if (!categoryChart) return;

        categoryChart.data.labels = data.labels || [];
        categoryChart.data.datasets[0].data = data.values || [];
        categoryChart.update();

    } catch (error) {
        console.error("Error gráfico:", error);
    }
}

/* ============================================
   REFRESH (SOLO CHART)
============================================ */

function refreshChart() {
    const selector = document.getElementById("chartSelector");
    if (!selector) return;
    loadChartData(selector.value);
}

/* ============================================
   EVENTOS (SOLO UNA VEZ)
============================================ */

function initRealtimeListeners() {
    if (realtimeInitialized) return;
    realtimeInitialized = true;

    document.body.addEventListener("inventory:refresh", () => {
        refreshChart();
    });

    document.body.addEventListener("notifications:updated", () => {
        // opcional
    });
}

/* ============================================
   INIT
============================================ */

function initView() {
    initMainSections();
    initSubSections();
    initChart();
}

function initOnce() {
    initRealtimeListeners();
}

// 🔥 EXPONER GLOBAL (clave para HTMX)
window.initView = initView;

document.addEventListener("DOMContentLoaded", () => {
    initOnce();
    initView();
});

document.body.addEventListener("htmx:afterSwap", (e) => {
    if (e.target.id === "app") {
        initView();
    }
});