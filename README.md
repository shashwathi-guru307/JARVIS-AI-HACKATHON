
# J.A.R.V.I.S. AI Core — Day 1

**Just A Rather Very Intelligent System**

An AI-powered monitoring and decision-support backend built with FastAPI and OpenAI.

---

## What is J.A.R.V.I.S.?

J.A.R.V.I.S. accepts any event or sensor reading as plain text, sends it to an LLM
with a structured system prompt, and returns a risk assessment as validated JSON —
including severity, explanation, and recommended action.

---

## Day 1 Objective

Build the foundational backend:

```
User → FastAPI → AI Agent → Analysis → Structured JSON Response
```

No frontend, no database, no ML — pure backend foundation.

---

## Architecture

```
User
  ↓
FastAPI
  ↓
Agent Route  (/agent/analyze)
  ↓
AI Service   (ai_service.py)
  ↓
LLM          (OpenAI)
  ↓
Structured JSON
  ↓
User
```

---

## Folder Structure

```
jarvis-hackathon/
├── backend/
│   ├── main.py              ← App init, route registration
│   ├── routes/
│   │   ├── health.py        ← GET /health
│   │   └── agent.py         ← POST /agent/analyze
│   ├── services/
│   │   └── ai_service.py    ← All LLM communication
│   ├── models/
│   │   └── agent_models.py  ← Pydantic request/response models
│   └── utils/
│       └── config.py        ← Environment variable loading
├── .env                     ← Your secrets (never commit this)
├── .env.example             ← Template for other developers
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/jarvis-hackathon.git
cd jarvis-hackathon

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Open .env and add your real OpenAI API key
```

---

## Environment Variables

| Variable    | Description              | Example      |
|-------------|--------------------------|--------------|
| AI_API_KEY  | Your OpenAI API key      | sk-...       |
| AI_MODEL    | Model to use             | gpt-4o       |

---

## Start the Server

```bash
uvicorn backend.main:app --reload
```

Visit: http://localhost:8000/docs

---

## API Endpoints

### GET /health
Returns system status. Always available.

```json
{
  "status": "online",
  "system": "J.A.R.V.I.S.",
  "version": "1.0.0"
}
```

### POST /agent/analyze
Analyze any event or sensor reading.

**Request:**
```json
{
  "message": "Machine temperature is 96°C and vibration is 0.92"
}
```

**Response:**
```json
{
  "status": "success",
  "risk_level": "HIGH",
  "summary": "Machine temperature and vibration are above safe thresholds.",
  "reason": "A temperature of 96°C combined with vibration of 0.92 suggests abnormal mechanical stress.",
  "recommended_action": "Shut down the machine and inspect cooling and mechanical components.",
  "confidence": 0.93
}
```

---

## Test Cases

| Input | Expected risk_level |
|-------|-------------------|
| Machine temp 72°C, vibration 0.2 | NORMAL or LOW |
| Machine temp 95°C, vibration 0.9 | HIGH or CRITICAL |
| Heart rate 110 BPM, SpO2 93% | MEDIUM (no diagnosis) |
| Transaction ₹95,000, normal < ₹2,000 | HIGH |

---

## Future Features (Day 2+)

- MQTT sensor integration
- Real-time WebSocket streaming
- PostgreSQL event logging
- Computer vision anomaly detection
- Multi-agent architecture
- Frontend dashboard
▶️ How to Run and Test
Install and start:
cd jarvis-hackathon
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Add your OpenAI API key to .env
uvicorn backend.main:app --reload

# Day 2 Features

Day 2 extends the J.A.R.V.I.S. AI Core with a real-time telemetry monitoring and anomaly detection pipeline.

## Day 2 Features

- Synthetic telemetry generator
- Pydantic telemetry validation
- Rule-based anomaly detection
- WebSocket streaming
- Latest telemetry endpoint
- Telemetry status endpoint
- Multiple WebSocket clients
- Error handling

## Day 2 Architecture

```text
┌──────────────────────┐
│ Synthetic Telemetry  │
│      Generator       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Telemetry Service    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Anomaly Detection    │
│    Rule Engine       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ FastAPI WebSocket    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ WebSocket Clients    │
└──────────────────────┘

