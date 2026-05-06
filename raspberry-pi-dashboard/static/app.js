/* --------------------------------------------------------------------
 * AR IoT Smart Home Dashboard - frontend logic
 * -------------------------------------------------------------------- */

const REFRESH_INTERVAL_MS = 5000;
const HISTORY_LIMIT = 50;

let historyChart = null;
let currentField = "temperature";
let currentLabel = "Temperature";
let currentUnit = "\u00b0C";
let currentColor = "#f97316";

/* ---------------- Utility ---------------- */

function setStatus(online) {
    const indicator = document.getElementById("status-indicator");
    const text = document.getElementById("status-text");
    if (!indicator || !text) return;

    indicator.classList.toggle("online", online);
    indicator.classList.toggle("offline", !online);
    text.textContent = online ? "Connected" : "Disconnected";
}

function updateLastUpdated() {
    const el = document.getElementById("last-updated");
    if (!el) return;
    el.textContent = new Date().toLocaleTimeString("en-GB", { hour12: false });
}

function formatTimestamp(ts) {
    // SQLite CURRENT_TIMESTAMP returns a UTC string "YYYY-MM-DD HH:MM:SS"
    if (!ts) return "";
    const d = new Date(ts.replace(" ", "T") + "Z");
    if (isNaN(d.getTime())) return ts;
    return d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false });
}

function hexToRgba(hex, alpha) {
    const h = hex.replace("#", "");
    const r = parseInt(h.substring(0, 2), 16);
    const g = parseInt(h.substring(2, 4), 16);
    const b = parseInt(h.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

async function fetchJson(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

/* ---------------- Latest values ---------------- */

async function fetchLatest() {
    const data = await fetchJson("/api/latest");

    document.getElementById("temperature-value").textContent =
        data.temperature !== undefined ? Number(data.temperature).toFixed(1) : "--";
    document.getElementById("humidity-value").textContent =
        data.humidity !== undefined ? Number(data.humidity).toFixed(1) : "--";
    document.getElementById("light-value").textContent =
        data.light !== undefined ? data.light : "--";
    document.getElementById("distance-value").textContent =
        data.distance !== undefined ? data.distance : "--";
}

/* ---------------- Alarms ---------------- */

function updateAlarmBox(elementId, alarmData) {
    const box = document.getElementById(elementId);
    if (!box || !alarmData) return;
    box.textContent = alarmData.message || "No alert.";
    box.classList.toggle("alert", !!alarmData.active);
    box.classList.toggle("normal", !alarmData.active);
}

async function fetchAlarms() {
    const data = await fetchJson("/api/alarms");

    updateAlarmBox("alarm-temperature", data.temperature);
    updateAlarmBox("alarm-humidity", data.humidity);
    updateAlarmBox("alarm-light", data.light);
    updateAlarmBox("alarm-distance", data.distance);

    if (data.thresholds) {
        ["temperature", "humidity", "light", "distance"].forEach(field => {
            const input = document.getElementById(`threshold-${field}`);
            // Don't overwrite the input while the user is typing in it
            if (input && document.activeElement !== input) {
                input.value = Number(data.thresholds[field]).toFixed(1);
            }
        });
    }
}

async function saveThreshold(field) {
    const input = document.getElementById(`threshold-${field}`);
    if (!input) return;

    try {
        await fetchJson("/api/settings/thresholds", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field, value: input.value })
        });
        await fetchAlarms();
    } catch (err) {
        console.error("Failed to save threshold:", err);
    }
}

/* ---------------- History chart ---------------- */

function buildChartConfig(labels, values) {
    return {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `${currentLabel} [${currentUnit}]`,
                data: values,
                tension: 0.35,
                borderColor: currentColor,
                backgroundColor: hexToRgba(currentColor, 0.15),
                pointBackgroundColor: currentColor,
                pointBorderColor: currentColor,
                pointRadius: 2.5,
                pointHoverRadius: 5,
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: "index" },
            animation: { duration: 400 },
            plugins: {
                legend: {
                    labels: { color: "#94a3b8", font: { family: "Outfit", size: 12 } }
                },
                tooltip: {
                    backgroundColor: "#121826",
                    borderColor: "rgba(255,255,255,0.1)",
                    borderWidth: 1,
                    titleColor: "#f1f5f9",
                    bodyColor: "#cbd5e1",
                    padding: 12,
                    displayColors: false,
                    titleFont: { family: "Outfit" },
                    bodyFont: { family: "JetBrains Mono", size: 12 }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#64748b",
                        maxTicksLimit: 8,
                        font: { family: "JetBrains Mono", size: 10 }
                    },
                    grid: { color: "rgba(255,255,255,0.04)" }
                },
                y: {
                    ticks: {
                        color: "#64748b",
                        font: { family: "JetBrains Mono", size: 10 }
                    },
                    grid: { color: "rgba(255,255,255,0.04)" }
                }
            }
        }
    };
}

async function fetchHistory() {
    const data = await fetchJson(`/api/history?limit=${HISTORY_LIMIT}`);

    const labels = data.map(item => formatTimestamp(item.timestamp));
    const values = data.map(item => Number(item[currentField]));

    const chartTitle = document.getElementById("chart-title");
    if (chartTitle) {
        chartTitle.textContent = `History chart \u2014 ${currentLabel.toLowerCase()}`;
    }

    const canvas = document.getElementById("history-chart");
    if (!canvas || typeof Chart === "undefined") return;

    // If the chart already exists, just update it -> no flicker, better performance
    if (historyChart) {
        const ds = historyChart.data.datasets[0];
        historyChart.data.labels = labels;
        ds.data = values;
        ds.label = `${currentLabel} [${currentUnit}]`;
        ds.borderColor = currentColor;
        ds.backgroundColor = hexToRgba(currentColor, 0.15);
        ds.pointBackgroundColor = currentColor;
        ds.pointBorderColor = currentColor;
        historyChart.update("none");
        return;
    }

    const ctx = canvas.getContext("2d");
    historyChart = new Chart(ctx, buildChartConfig(labels, values));
}

/* ---------------- Chart switcher ---------------- */

function setupChartButtons() {
    const buttons = document.querySelectorAll(".chart-button");
    buttons.forEach(button => {
        button.addEventListener("click", async () => {
            buttons.forEach(b => b.classList.remove("active"));
            button.classList.add("active");

            currentField = button.dataset.field;
            currentLabel = button.dataset.label;
            currentUnit = button.dataset.unit;
            currentColor = button.dataset.color || "#38bdf8";

            try {
                await fetchHistory();
            } catch (err) {
                console.error("Failed to load history:", err);
            }
        });
    });
}

/* ---------------- Main loop ---------------- */

async function refreshDashboard() {
    try {
        await Promise.all([fetchLatest(), fetchAlarms(), fetchHistory()]);
        setStatus(true);
        updateLastUpdated();
    } catch (err) {
        console.error("Refresh failed:", err);
        setStatus(false);
    }
}

// Expose globally for inline onclick="saveThreshold(...)"
window.saveThreshold = saveThreshold;

setupChartButtons();
refreshDashboard();
setInterval(refreshDashboard, REFRESH_INTERVAL_MS);
