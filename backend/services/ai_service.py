import os
import json

from dotenv import load_dotenv

from groq import Groq
from groq import APIConnectionError, APITimeoutError, AuthenticationError

from backend.models.agent_models import AgentResponse

load_dotenv()


# =========================
# Configuration
# =========================

def get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured in .env."
        )

    return api_key


def get_model() -> str:
    return os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )


# =========================
# System Prompt
# =========================

SYSTEM_PROMPT = """
You are J.A.R.V.I.S., an intelligent AI assistant.

Analyze the event provided by the user and return ONLY valid JSON
matching the AgentResponse schema. Use exactly these keys:
status, risk_level, summary, reason, recommended_action, confidence.
Set status to "success" for a completed analysis.
"""


def _normalise_response_data(data: object) -> dict:
    """Accept common LLM key/value variations without weakening validation."""
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object")

    aliases = {
        "riskLevel": "risk_level",
        "risk": "risk_level",
        "recommendedAction": "recommended_action",
        "action": "recommended_action",
    }
    normalised = {aliases.get(key, key): value for key, value in data.items()}

    status = normalised.get("status")
    if status is None:
        normalised["status"] = "success"
    else:
        status = str(status).strip().lower()
        normalised["status"] = {
            "ok": "success",
            "completed": "success",
            "success": "success",
            "failed": "error",
            "failure": "error",
            "error": "error",
        }.get(status, status)

    risk_level = normalised.get("risk_level")
    if risk_level is not None:
        normalised["risk_level"] = {
            "normal": "NORMAL",
            "low": "LOW",
            "medium": "MEDIUM",
            "moderate": "MEDIUM",
            "high": "HIGH",
            "critical": "CRITICAL",
            "severe": "CRITICAL",
        }.get(str(risk_level).strip().lower(), risk_level)

    confidence = normalised.get("confidence")
    if isinstance(confidence, str):
        confidence = confidence.strip().removesuffix("%")
        try:
            confidence = float(confidence)
        except ValueError:
            pass
        else:
            if confidence > 1:
                confidence /= 100
            normalised["confidence"] = confidence

    return normalised


# =========================
# AI Analysis
# =========================

def analyze_event(message: str) -> AgentResponse:

    # 1. Validate configuration
    try:
        api_key = get_api_key()
    except ValueError as e:
        return AgentResponse(
            status="error",
            error=str(e)
        )

    model = get_model()

    # 2. Call Groq
    try:
        client = Groq(
            api_key=api_key,
            timeout=30.0
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Analyze the following event:\n\n{message}"
                }
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

    except AuthenticationError:
        return AgentResponse(
            status="error",
            error="Authentication failed. Check your GROQ_API_KEY in .env."
        )

    except APITimeoutError:
        return AgentResponse(
            status="error",
            error="The Groq AI service timed out. Please try again."
        )

    except APIConnectionError:
        return AgentResponse(
            status="error",
            error="Could not connect to Groq AI. Check your internet connection."
        )

    except Exception as e:
        return AgentResponse(
            status="error",
            error=f"Groq AI request failed: {str(e)}"
        )

    # 3. Extract JSON
    raw_content = response.choices[0].message.content or ""

    try:
        data = json.loads(raw_content)
        data = _normalise_response_data(data)
    except (json.JSONDecodeError, ValueError):
        return AgentResponse(
            status="error",
            error="AI returned a response that could not be parsed as JSON."
        )

    # 4. Validate AgentResponse
    try:
        return AgentResponse.model_validate(data)
    except Exception:
        return AgentResponse(
            status="error",
            error="AI response did not match the expected schema."
        )