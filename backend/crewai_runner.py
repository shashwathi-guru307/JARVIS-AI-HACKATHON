"""
J.A.R.V.I.S. AI Flow Runner

Local implementation of the J.A.R.V.I.S. command flow.

CrewAI is not required for the local application.
The runner uses the existing Groq-powered AI service and
injects the live system snapshot into the AI context.
"""

import asyncio
import logging
import json

from backend.services.ai_service import analyze_event
from backend.services.orchestrator import get_system_snapshot

logger = logging.getLogger(__name__)


async def run_flow(
    message: str,
    mode: str = "analyze",
    system_context: str = "",
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    Run the J.A.R.V.I.S. AI flow without requiring CrewAI.

    mode="analyze":
        Returns structured AI analysis.

    mode="chat":
        Returns a conversational J.A.R.V.I.S. response using
        live system context.
    """

    if conversation_history is None:
        conversation_history = []

    # Keep only the latest 12 messages.
    trimmed_history = conversation_history[-12:]

    def _run():
        try:
            # -------------------------------------------------
            # Get live system context if frontend did not provide it
            # -------------------------------------------------
            if not system_context:
                try:
                    snapshot = get_system_snapshot()

                    system_context_local = (
                        f"System status: {snapshot.get('system_status')}. "
                        f"System risk: {snapshot.get('system_risk')}. "
                        f"System score: {snapshot.get('system_score')}. "
                        f"Priority: {snapshot.get('priority')}. "
                        f"Active alerts: {snapshot.get('active_alerts')}. "
                        f"Domain risks: "
                        f"{json.dumps(snapshot.get('domain_risks', {}))}. "
                        f"Correlated conditions: "
                        f"{'; '.join(snapshot.get('correlated_conditions', []))}. "
                        f"Recommendation: "
                        f"{snapshot.get('recommendation')}. "
                        f"Contributing factors: "
                        f"{'; '.join(snapshot.get('contributing_factors', []))}."
                    )

                except Exception as e:
                    logger.warning(
                        "Could not build system snapshot: %s",
                        e,
                    )
                    system_context_local = "Live system context unavailable."

            else:
                system_context_local = system_context

            # -------------------------------------------------
            # Conversation history
            # -------------------------------------------------
            history_text = ""

            if trimmed_history:
                history_lines = []

                for item in trimmed_history:
                    role = item.get("role", "user")
                    content = item.get("content", "")

                    if content:
                        history_lines.append(
                            f"{role.upper()}: {content}"
                        )

                history_text = "\n".join(history_lines)

            # -------------------------------------------------
            # CHAT MODE
            # -------------------------------------------------
            if mode == "chat":

                prompt = f"""
You are J.A.R.V.I.S., the intelligent command assistant
for an industrial monitoring system.

Answer the user's question naturally and clearly.

Use the LIVE SYSTEM CONTEXT below as the source of truth.
Do not invent telemetry, alerts, risks, or system conditions.

LIVE SYSTEM CONTEXT:
{system_context_local}

CONVERSATION HISTORY:
{history_text if history_text else "No previous conversation."}

USER:
{message}

Instructions:
- Answer directly.
- Be concise but informative.
- Mention important risks or alerts when relevant.
- If the system is healthy, say so clearly.
- If something requires attention, explain what and why.
- Do not mention CrewAI.
- Do not mention internal implementation details.
"""

                ai_result = analyze_event(prompt)

                if ai_result.status == "error":
                    return {
                        "mode": "chat",
                        "status": "error",
                        "error": ai_result.error,
                    }

                # Build a natural J.A.R.V.I.S. response
                response_parts = []

                if ai_result.summary:
                    response_parts.append(
                        ai_result.summary
                    )

                if ai_result.reason:
                    response_parts.append(
                        f"Reason: {ai_result.reason}"
                    )

                if ai_result.recommended_action:
                    response_parts.append(
                        f"Recommendation: {ai_result.recommended_action}"
                    )

                response_text = " ".join(response_parts)

                return {
                    "mode": "chat",
                    "status": "success",
                    "response": response_text,
                    "speak": response_text,
                    "risk_level": ai_result.risk_level,
                    "confidence": ai_result.confidence,
                    "context_used": system_context_local,
                }

            # -------------------------------------------------
            # ANALYZE MODE
            # -------------------------------------------------
            else:

                prompt = f"""
Analyze the following J.A.R.V.I.S. command using the
live system context.

LIVE SYSTEM CONTEXT:
{system_context_local}

CONVERSATION HISTORY:
{history_text if history_text else "No previous conversation."}

USER COMMAND:
{message}

Return the appropriate structured analysis.

Do not invent system data.
Use the live context when answering.
"""

                ai_result = analyze_event(prompt)

                if ai_result.status == "error":
                    return {
                        "mode": "analyze",
                        "status": "error",
                        "error": ai_result.error,
                    }

                return {
                    "mode": "analyze",
                    "status": "success",
                    "risk_level": ai_result.risk_level,
                    "summary": ai_result.summary,
                    "reason": ai_result.reason,
                    "recommended_action": ai_result.recommended_action,
                    "confidence": ai_result.confidence,
                    "context_used": system_context_local,
                }

        except Exception as e:
            logger.exception("J.A.R.V.I.S. flow error")

            return {
                "status": "error",
                "error": str(e),
            }

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        None,
        _run,
    )