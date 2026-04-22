let historyChart = null;
let currentField = "temperature";
let currentLabel = "Teplota";
let currentUnit = "°C";

async function fetchLatest() {
    const response = await fetch("/api/latest");
    const data = await response.json();

    document.getElementById("temperature-value").textContent =
        data.temperature !== undefined ? `${Number(data.temperature).toFixed(1)} °C` : "-- °C";
    document.getElementById("humidity-value").textContent =
        data.humidity !== undefined ? `${Number(data.humidity).toFixed(1)} %` : "-- %";
    document.getElementById("light-value").textContent =
        data.light !== undefined ? `${data.light} %` : "-- %";
    document.getElementById("distance-value").textContent =
        data.distance !== undefined ? `${data.distance} cm` : "-- cm";
}

function updateAlarmBox(elementId, alarmData) {
    const box = document.getElementById(elementId);
    if (!box) return;

    box.textContent = alarmData.message || "Bez alarmu.";

    if (alarmData.active) {
        box.classList.remove("normal");
        box.classList.add("alert");
    } else {
        box.classList.remove("alert");
        box.classList.add("normal");
    }
}

async function fetchAlarms() {
    const response = await fetch("/api/alarms");
    const data = await response.json();

    updateAlarmBox("alarm-temperature", data.temperature);
    updateAlarmBox("alarm-humidity", data.humidity);
    updateAlarmBox("alarm-light", data.light);
    updateAlarmBox("alarm-distance", data.distance);

    if (data.thresholds) {
        document.getElementById("threshold-temperature").value = Number(data.thresholds.temperature).toFixed(1);
        document.getElementById("threshold-humidity").value = Number(data.thresholds.humidity).toFixed(1);
        document.getElementById("threshold-light").value = Number(data.thresholds.light).toFixed(1);
        document.getElementById("threshold-distance").value = Number(data.thresholds.distance).toFixed(1);
    }
}

async function saveThreshold(field) {
    const input = document.getElementById(`threshold-${field}`);
    const value = input.value;

    await fetch("/api/settings/thresholds", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ field, value })
    });

    await fetchAlarms();
}

async function fetchHistory() {
    const response = await fetch("/api/history?limit=30");
    const data = await response.json();

    const labels = data.map(item => item.timestamp);
    const values = data.map(item => Number(item[currentField]));

    const chartTitle = document.getElementById("chart-title");
    if (chartTitle) {
        chartTitle.textContent = `Historicky graf - ${currentLabel.toLowerCase()}`;
    }

    const canvas = document.getElementById("history-chart");
    if (!canvas) return;
    if (typeof Chart === "undefined") return;

    const ctx = canvas.getContext("2d");

    if (historyChart) {
        historyChart.destroy();
    }

    historyChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `${currentLabel} [${currentUnit}]`,
                data: values,
                tension: 0.3,
                borderColor: "#38bdf8",
                backgroundColor: "rgba(56, 189, 248, 0.2)",
                pointBackgroundColor: "#38bdf8",
                pointBorderColor: "#38bdf8"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: "#f3f4f6"
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#f3f4f6",
                        maxTicksLimit: 6
                    },
                    grid: {
                        color: "#374151"
                    }
                },
                y: {
                    ticks: {
                        color: "#f3f4f6"
                    },
                    grid: {
                        color: "#374151"
                    }
                }
            }
        }
    });
}

function setupChartButtons() {
    const buttons = document.querySelectorAll(".chart-button");

    buttons.forEach(button => {
        button.addEventListener("click", async () => {
            buttons.forEach(b => b.classList.remove("active"));
            button.classList.add("active");

            currentField = button.dataset.field;
            currentLabel = button.dataset.label;
            currentUnit = button.dataset.unit;

            await fetchHistory();
        });
    });
}

async function refreshDashboard() {
    await fetchLatest();
    await fetchAlarms();
    await fetchHistory();
}

setupChartButtons();
refreshDashboard();
setInterval(refreshDashboard, 5000);