let categoryChart = null;
let realtimeInitialized = false;

function setCategoryChart(chart) {
    categoryChart = chart;
}

function setRealtimeInitialized(value) {
    realtimeInitialized = value;
}

window.dashboardState = {
    get categoryChart() {
        return categoryChart;
    },
    get realtimeInitialized() {
        return realtimeInitialized;
    },
    setCategoryChart,
    setRealtimeInitialized
};