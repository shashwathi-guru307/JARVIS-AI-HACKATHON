import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.models.telemetry_models import (
    TelemetryData,
    TelemetryResponse,
    TelemetryValues,
    AnomalyAnalysis,
)

from backend.services.anomaly_service import detect_anomaly
from data.generator import generate_telemetry


router = APIRouter()

logger = logging.getLogger(__name__)


# Stores only the most recently generated telemetry event
latest_telemetry = None

# Current number of connected WebSocket clients
connected_clients = 0


@router.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):

    global latest_telemetry, connected_clients

    # --------------------------------------------------
    # CLIENT CONNECTION
    # --------------------------------------------------
    try:
        await websocket.accept()

    except Exception as error:
        logger.error(
            "Failed to accept WebSocket connection: %s",
            error,
        )
        return

    connected_clients += 1

    logger.info(
        "WebSocket client connected | total_clients=%d",
        connected_clients,
    )

    try:

        # --------------------------------------------------
        # TELEMETRY STREAM
        # --------------------------------------------------
        while True:

            try:
                # Generate telemetry
                raw_telemetry = generate_telemetry("MACHINE_01")

                logger.info(
                    "Generated telemetry for MACHINE_01"
                )

            except Exception as error:

                logger.exception(
                    "Telemetry generator error: %s",
                    error,
                )

                # Do not crash the server.
                # Wait and try generating another reading.
                await asyncio.sleep(1)
                continue


            # --------------------------------------------------
            # TELEMETRY VALIDATION
            # --------------------------------------------------
            try:

                telemetry = TelemetryData(**raw_telemetry)

            except Exception as error:

                logger.error(
                    "Invalid telemetry received: %s",
                    error,
                )

                # Ignore this invalid reading
                # and continue the stream.
                await asyncio.sleep(1)
                continue


            # --------------------------------------------------
            # ANOMALY DETECTION
            # --------------------------------------------------
            try:

                analysis = detect_anomaly(telemetry)

            except Exception as error:

                logger.exception(
                    "Anomaly detection error: %s",
                    error,
                )

                # Do not terminate the client connection.
                await asyncio.sleep(1)
                continue


            # --------------------------------------------------
            # LOG ANOMALIES
            # --------------------------------------------------
            for reason in analysis["reasons"]:

                if "Temperature" in reason:

                    logger.warning(
                        "High temperature detected | "
                        "device=%s temperature=%.2f",
                        telemetry.device_id,
                        telemetry.temperature,
                    )

                elif "Vibration" in reason:

                    logger.warning(
                        "High vibration detected | "
                        "device=%s vibration=%.2f",
                        telemetry.device_id,
                        telemetry.vibration,
                    )

                elif "Battery" in reason:

                    logger.warning(
                        "Low battery detected | "
                        "device=%s battery=%.2f",
                        telemetry.device_id,
                        telemetry.battery,
                    )


            # --------------------------------------------------
            # BUILD RESPONSE
            # --------------------------------------------------
            try:

                response = TelemetryResponse(
                    device_id=telemetry.device_id,
                    timestamp=telemetry.timestamp,

                    telemetry=TelemetryValues(
                        temperature=telemetry.temperature,
                        humidity=telemetry.humidity,
                        pressure=telemetry.pressure,
                        vibration=telemetry.vibration,
                        rpm=telemetry.rpm,
                        battery=telemetry.battery,
                    ),

                    analysis=AnomalyAnalysis(
                        status=analysis["status"],
                        risk_level=analysis["risk_level"],
                        reasons=analysis["reasons"],
                    ),
                )

            except Exception as error:

                logger.exception(
                    "Failed to build telemetry response: %s",
                    error,
                )

                await asyncio.sleep(1)
                continue


            # --------------------------------------------------
            # STORE LATEST TELEMETRY
            # --------------------------------------------------
            latest_telemetry = {
                "device_id": telemetry.device_id,
                "temperature": telemetry.temperature,
                "vibration": telemetry.vibration,
                "rpm": telemetry.rpm,
                "status": analysis["status"],
            }


            # --------------------------------------------------
            # SEND TO CLIENT
            # --------------------------------------------------
            try:

                await websocket.send_json(
                    response.model_dump(mode="json")
                )

            except WebSocketDisconnect:

                logger.info(
                    "WebSocket client disconnected during send"
                )

                break

            except Exception as error:

                logger.error(
                    "Failed to send telemetry to client: %s",
                    error,
                )

                break


            # --------------------------------------------------
            # WAIT FOR NEXT READING
            # --------------------------------------------------
            try:

                await asyncio.sleep(1)

            except asyncio.CancelledError:

                logger.info(
                    "Telemetry stream task cancelled"
                )

                break


    # ------------------------------------------------------
    # CLIENT DISCONNECTED
    # ------------------------------------------------------
    except WebSocketDisconnect:

        logger.info(
            "WebSocket client disconnected"
        )


    # ------------------------------------------------------
    # UNEXPECTED ERROR
    # ------------------------------------------------------
    except Exception as error:

        logger.exception(
            "Unexpected WebSocket error: %s",
            error,
        )


    # ------------------------------------------------------
    # ALWAYS CLEAN UP
    # ------------------------------------------------------
    finally:

        connected_clients = max(
            0,
            connected_clients - 1
        )

        logger.info(
            "WebSocket client removed | total_clients=%d",
            connected_clients,
        )


# ==========================================================
# GET LATEST TELEMETRY
# ==========================================================

@router.get("/telemetry/latest")
async def get_latest_telemetry():

    try:

        if latest_telemetry is None:

            return {
                "message": "No telemetry has been generated yet"
            }

        return latest_telemetry

    except Exception as error:

        logger.exception(
            "Failed to retrieve latest telemetry: %s",
            error,
        )

        return {
            "error": "Unable to retrieve latest telemetry"
        }


# ==========================================================
# TELEMETRY SYSTEM STATUS
# ==========================================================

@router.get("/telemetry/status")
async def get_telemetry_status():

    try:

        return {
            "streaming": connected_clients > 0,
            "connected_clients": connected_clients,
            "interval_seconds": 1,
            "devices": 1,
        }

    except Exception as error:

        logger.exception(
            "Failed to retrieve telemetry status: %s",
            error,
        )

        return {
            "error": "Unable to retrieve telemetry status"
        }