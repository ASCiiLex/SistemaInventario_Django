import { realtimeInitialized, setRealtimeInitialized } from "./state.js";
import { refreshChart } from "./chart.js";

export function initRealtimeListeners() {
    if (realtimeInitialized) return;

    setRealtimeInitialized(true);

    document.body.addEventListener("inventory:stock_changed", () => {
        refreshChart();
    });
}