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
}

export async function loadChartData(tipo) {
    try {
        const loader = document.getElementById("chart-loader");
        if (loader) loader.style.display = "flex";

        const url = window.dashboardChartUrl.replace("TIPO", tipo);

        const response = await fetch(url);

        if (!response.ok) {
            console.warn("Chart response no OK:", tipo, url);
            return;
        }

        const data = await response.json();

        if (!categoryChart) {
            initChart();
            return;
        }

        categoryChart.data.labels = data.labels || [];
        categoryChart.data.datasets[0].data = data.values || [];
        categoryChart.update();

    } catch (error) {
        console.error("Error gráfico:", error);
    } finally {
        const loader = document.getElementById("chart-loader");
        if (loader) loader.style.display = "none";
    }
}

export function refreshChart() {
    const selector = document.getElementById("chartSelector");
    if (!selector) return;

    loadChartData(selector.value);
}