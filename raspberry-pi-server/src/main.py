import asyncio
import json
from typing import Any

import serial
import websockets
from websockets.server import WebSocketServerProtocol

from config import HOST, PORT, SERIAL_PORT, SERIAL_BAUDRATE


clients: set[WebSocketServerProtocol] = set()
serial_connection: serial.Serial | None = None


def open_serial_connection() -> serial.Serial:
    return serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)


async def broadcast_json(payload: dict[str, Any]) -> None:
    if not clients:
        return

    message = json.dumps(payload)
    disconnected = set()

    for client in clients:
        try:
            await client.send(message)
        except Exception:
            disconnected.add(client)

    for client in disconnected:
        clients.discard(client)


def send_to_arduino(command: str) -> None:
    global serial_connection
    if serial_connection is None:
        raise RuntimeError("Serial connection is not initialized.")

    serial_connection.write((command + "\n").encode("utf-8"))
    serial_connection.flush()
    print(f"Sent to Arduino: {command}")


async def serial_reader_task() -> None:
    global serial_connection

    print(f"Opening serial port {SERIAL_PORT} at {SERIAL_BAUDRATE} baud...")
    serial_connection = open_serial_connection()

    await asyncio.sleep(2)
    print("Serial connection ready.")

    while True:
        try:
            if serial_connection.in_waiting > 0:
                line = serial_connection.readline().decode("utf-8", errors="ignore").strip()

                if not line:
                    await asyncio.sleep(0.05)
                    continue

                print(f"Serial received: {line}")

                try:
                    sensor_data = json.loads(line)

                    await broadcast_json({
                        "type": "sensor_data",
                        "payload": sensor_data
                    })

                except json.JSONDecodeError:
                    print("Ignoring non-JSON Arduino output:", line)

            await asyncio.sleep(0.05)

        except Exception as e:
            print("Serial read error:", e)
            await asyncio.sleep(1)


async def process_message(websocket: WebSocketServerProtocol, raw_message: str) -> None:
    print(f"WebSocket received: {raw_message}")

    try:
        message = json.loads(raw_message)
        message_type = message.get("type")

        if message_type == "control_command":
            command = message.get("command")

            if command == "servo":
                value = int(message.get("value", 0))
                value = max(0, min(180, value))
                send_to_arduino(f"S {value}")

                await websocket.send(json.dumps({
                    "type": "command_result",
                    "payload": {
                        "success": True,
                        "command": "servo",
                        "value": value,
                        "message": f"Servo set to {value}"
                    }
                }))

            elif command == "rgb":
                r = int(message.get("r", 0))
                g = int(message.get("g", 0))
                b = int(message.get("b", 0))

                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

                send_to_arduino(f"L {r} {g} {b}")

                await websocket.send(json.dumps({
                    "type": "command_result",
                    "payload": {
                        "success": True,
                        "command": "rgb",
                        "r": r,
                        "g": g,
                        "b": b,
                        "message": f"RGB set to {r}, {g}, {b}"
                    }
                }))

            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "payload": {
                        "message": f"Unsupported control command: {command}"
                    }
                }))

        else:
            await websocket.send(json.dumps({
                "type": "error",
                "payload": {
                    "message": f"Unsupported message type: {message_type}"
                }
            }))

    except json.JSONDecodeError:
        await websocket.send(json.dumps({
            "type": "error",
            "payload": {
                "message": "Invalid JSON message."
            }
        }))


async def handler(websocket: WebSocketServerProtocol) -> None:
    print("WebSocket client connected.")
    clients.add(websocket)

    await websocket.send(json.dumps({
        "type": "connection_ack",
        "payload": {
            "message": "Connected to Raspberry Pi WebSocket server."
        }
    }))

    try:
        async for message in websocket:
            await process_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket client disconnected.")
    finally:
        clients.discard(websocket)


async def main() -> None:
    print(f"Starting WebSocket server on ws://{HOST}:{PORT}")

    asyncio.create_task(serial_reader_task())

    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())