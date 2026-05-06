from flask import Flask, jsonify, render_template, request

from database import (
    get_latest_reading,
    get_recent_readings,
    get_alarm_thresholds,
    set_alarm_threshold,
    init_db,
)

VALID_FIELDS = ("temperature", "humidity", "light", "distance")

FIELD_META = {
    "temperature": {"unit": "\u00b0C", "direction": "above"},
    "humidity":    {"unit": "%",       "direction": "above"},
    "light":       {"unit": "%",       "direction": "below"},
    "distance":    {"unit": "cm",      "direction": "below"},
}

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/latest")
def api_latest():
    latest = get_latest_reading()
    return jsonify(latest or {})


@app.route("/api/history")
def api_history():
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 500))
    readings = get_recent_readings(limit=limit)
    return jsonify(readings)


def _evaluate_alarm(field: str, value: float, threshold: float) -> dict:
    meta = FIELD_META[field]
    if meta["direction"] == "above":
        active = value > threshold
    else:
        active = value < threshold

    return {
        "active": active,
        "value": value,
        "threshold": threshold,
        "message": f"{value:.1f} {meta['unit']} / threshold: {threshold:.1f} {meta['unit']}",
    }


@app.route("/api/alarms")
def api_alarms():
    latest = get_latest_reading()
    thresholds = get_alarm_thresholds()

    if not latest:
        empty = {"active": False, "message": "No data.", "value": None, "threshold": None}
        return jsonify({f: empty for f in VALID_FIELDS} | {"thresholds": thresholds})

    result = {
        field: _evaluate_alarm(field, float(latest[field]), thresholds[field])
        for field in VALID_FIELDS
    }
    result["thresholds"] = thresholds
    return jsonify(result)


@app.route("/api/settings/thresholds", methods=["GET", "POST"])
def api_thresholds():
    if request.method == "GET":
        return jsonify(get_alarm_thresholds())

    data = request.get_json(silent=True) or {}
    field = data.get("field")
    raw_value = data.get("value")

    if field not in VALID_FIELDS:
        return jsonify({"success": False, "message": "Unknown field."}), 400

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid value."}), 400

    set_alarm_threshold(field, value)
    return jsonify({"success": True, "field": field, "value": value})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
