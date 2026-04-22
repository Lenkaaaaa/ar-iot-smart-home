from flask import Flask, jsonify, render_template, request

from database import (
    get_latest_reading,
    get_recent_readings,
    get_alarm_thresholds,
    set_alarm_threshold,
    init_db,
)

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
    readings = get_recent_readings(limit=limit)
    return jsonify(readings)


@app.route("/api/alarms")
def api_alarms():
    latest = get_latest_reading()
    thresholds = get_alarm_thresholds()

    if not latest:
        return jsonify({
            "temperature": {"active": False, "message": "No data available."},
            "humidity": {"active": False, "message": "No data available."},
            "light": {"active": False, "message": "No data available."},
            "distance": {"active": False, "message": "No data available."},
            "thresholds": thresholds
        })

    temperature = float(latest["temperature"])
    humidity = float(latest["humidity"])
    light = float(latest["light"])
    distance = float(latest["distance"])

    return jsonify({
        "temperature": {
            "active": temperature > thresholds["temperature"],
            "message": f"Teplota: {temperature:.1f} °C / limit: {thresholds['temperature']:.1f} °C"
        },
        "humidity": {
            "active": humidity > thresholds["humidity"],
            "message": f"Vlhkost: {humidity:.1f} % / limit: {thresholds['humidity']:.1f} %"
        },
        "light": {
            "active": light < thresholds["light"],
            "message": f"Svetlo: {light:.1f} % / limit: {thresholds['light']:.1f} %"
        },
        "distance": {
            "active": distance < thresholds["distance"],
            "message": f"Vzdialenost: {distance:.1f} cm / limit: {thresholds['distance']:.1f} cm"
        },
        "thresholds": thresholds
    })


@app.route("/api/settings/thresholds", methods=["GET", "POST"])
def api_thresholds():
    if request.method == "GET":
        return jsonify(get_alarm_thresholds())

    data = request.get_json(silent=True) or {}
    field = data.get("field")
    value = data.get("value")

    try:
        value = float(value)
        set_alarm_threshold(field, value)
    except Exception:
        return jsonify({
            "success": False,
            "message": "Invalid field or value."
        }), 400

    return jsonify({
        "success": True,
        "field": field,
        "value": value
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)