import asyncio
import json
from datetime import datetime

import websockets


WEBSOCKET_URL = "ws://localhost:8000/ws/telemetry"


async def telemetry_client():
    print(f"Connecting to {WEBSOCKET_URL}...")

    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:

            print()
            print("Connected to J.A.R.V.I.S. telemetry stream")
            print()

            while True:
                message = await websocket.recv()

                data = json.loads(message)

                timestamp = datetime.fromisoformat(
                    data["timestamp"]
                ).strftime("%H:%M:%S")

                telemetry = data["telemetry"]
                analysis = data["analysis"]

                print(f"[{timestamp}]")
                print(f"Device: {data['device_id']}")
                print(f"Temperature: {telemetry['temperature']}°C")
                print(f"Vibration: {telemetry['vibration']}")
                print(f"RPM: {telemetry['rpm']}")
                print(f"Status: {analysis['status']}")
                print()

    except websockets.exceptions.ConnectionClosed:
        print("🔌 Connection closed by server.")

    except ConnectionRefusedError:
        print("❌ Could not connect to J.A.R.V.I.S.")
        print("Make sure the FastAPI server is running.")

    except Exception as error:
        print(f"❌ WebSocket client error: {error}")


if __name__ == "__main__":
    asyncio.run(telemetry_client())