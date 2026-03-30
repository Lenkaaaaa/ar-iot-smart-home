import asyncio
import json
from typing import Any

import serial
import websockets
from websockets.server import WebSocketServerProtocol

from config import HOST, PORT, SERIAL_PORT, SERIAL_BAUDRATE


clients: set[WebSocketServerProtocol] = set()


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


async def serial_reader_task() -> None:
    print(f"Opening serial port {SERIAL_PORT} at {SERIAL_BAUDRATE} baud...")
    ser = open_serial_connection()

    await asyncio.sleep(2)
    print("Serial connection ready.")

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

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
                    print("Invalid JSON from Arduino:", line)

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
            value = message.get("value")

            await websocket.send(json.dumps({
                "type": "command_result",
                "payload": {
                    "success": True,
                    "command": command,
                    "value": value,
                    "message": "Command received by Raspberry Pi."
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

    serial_task = asyncio.create_task(serial_reader_task())

    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())