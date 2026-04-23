import { categoryChart, setCategoryChart } from "./state.js";

function initChartSelector() {
    const selector = document.getElementById("chartSelector");
    if (!selector) return;

    if (selector.dataset.bound === "true") return;
    selector.dataset.bound = "true";

    selector.addEventListener("change", function () {
        loadChartData(this.value);
    });
}

export function initChart() {
    const canvas = document.getElementById("categoryChart");
    if (!canvas || !window.chartData) return;

    const labels = window.chartData.labels || [];
    const values = window.chartData.values || [];

    // ❌ eliminamos el bloqueo
    // if (!labels.length) return;

    if (categoryChart) {
        categoryChart.destroy();
    }

    const chart = new Chart(canvas, {
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
            animation: false,
            scales: { x: { beginAtZero: true } }
        }
    });

    setCategoryChart(chart);
    initChartSelector();

    // 🔥 IMPORTANTE: cargar datos reales siempre
    loadChartData("categorias");
}