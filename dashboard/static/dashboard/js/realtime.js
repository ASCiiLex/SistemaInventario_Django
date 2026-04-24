function initRealtimeListeners() {
    if (window.dashboardState.realtimeInitialized) return;

    window.dashboardState.setRealtimeInitialized(true);

    document.body.addEventListener("inventory:stock_changed", () => {
        if (window.refreshChart) {
            window.refreshChart();
        }
    });
}

window.initRealtimeListeners = initRealtimeListeners;