import { initMainSections, initSubSections } from "./ui.js";
import { initChart } from "./chart.js";
import { initRealtimeListeners } from "./realtime.js";

function initView() {
    initMainSections();
    initSubSections();
    initChart();
}

function initOnce() {
    initRealtimeListeners();
}

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