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

function applyEmptyState(chart) {
    chart.data.labels = ["Sin datos"];
    chart.data.datasets[0].data = [0];
}

export function initChart() {
    const canvas = document.getElementById("categoryChart");
    if (!canvas || !window.chartData) return;

    let labels = window.chartData.labels || [];
    let values = window.chartData.values || [];

    if (categoryChart) {
        categoryChart.destroy();
    }

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels.length ? labels : ["Sin datos"],
            datasets: [{
                label: "Stock",
                data: values.length ? values : [0],
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

        const labels = data.labels || [];
        const values = data.values || [];

        if (!labels.length) {
            applyEmptyState(categoryChart);
        } else {
            categoryChart.data.labels = labels;
            categoryChart.data.datasets[0].data = values;
        }

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