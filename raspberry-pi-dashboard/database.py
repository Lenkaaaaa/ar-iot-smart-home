import os
import sqlite3
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "sensor_data.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                light INTEGER NOT NULL,
                distance INTEGER NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        defaults = {
            "temperature_alarm_threshold": "30.0",
            "humidity_alarm_threshold": "70.0",
            "light_alarm_threshold": "30.0",
            "distance_alarm_threshold": "10.0",
        }

        for key, value in defaults.items():
            conn.execute(
                """
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (?, ?)
                """,
                (key, value),
            )

        conn.commit()


def insert_reading(
    temperature: float,
    humidity: float,
    light: int,
    distance: int,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sensor_readings (temperature, humidity, light, distance)
            VALUES (?, ?, ?, ?)
            """,
            (temperature, humidity, light, distance),
        )
        conn.commit()


def get_latest_reading() -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, timestamp, temperature, humidity, light, distance
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    return dict(row) if row else None


def get_recent_readings(limit: int = 50) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, timestamp, temperature, humidity, light, distance
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    result = [dict(row) for row in rows]
    result.reverse()
    return result


def get_setting_float(key: str, default: float) -> float:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        ).fetchone()

    return float(row["value"]) if row else default


def set_setting_float(key: str, value: float) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, str(value)),
        )
        conn.commit()


def get_alarm_thresholds() -> dict[str, float]:
    return {
        "temperature": get_setting_float("temperature_alarm_threshold", 30.0),
        "humidity": get_setting_float("humidity_alarm_threshold", 70.0),
        "light": get_setting_float("light_alarm_threshold", 30.0),
        "distance": get_setting_float("distance_alarm_threshold", 10.0),
    }


def set_alarm_threshold(field: str, value: float) -> None:
    key_map = {
        "temperature": "temperature_alarm_threshold",
        "humidity": "humidity_alarm_threshold",
        "light": "light_alarm_threshold",
        "distance": "distance_alarm_threshold",
    }

    key = key_map.get(field)
    if not key:
        raise ValueError(f"Unsupported field: {field}")

    set_setting_float(key, value)