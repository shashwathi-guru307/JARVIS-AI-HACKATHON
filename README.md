# X.A.Z.E.L.

## AI-Powered Autonomous Incident Resolution for Smart Manufacturing

X.A.Z.E.L. is an AI-powered incident intelligence and resolution platform designed for **smart manufacturing environments**.

It addresses a common operational problem: a single machine issue can generate multiple alerts across telemetry, maintenance, safety, energy, and other monitoring systems. Instead of treating each alert independently, X.A.Z.E.L. correlates related signals into a single incident, investigates the available evidence, identifies a probable root cause, assesses production impact, prioritizes the incident, recommends remediation, manages human approval, performs a safe simulated action, verifies the result, and records the complete audit trail.

> **Hackathon Prototype:** This project is a software prototype for demonstrating autonomous incident-resolution workflows. It is not a certified industrial control system, medical system, or real emergency-response system.

---

## 🎯 Problem

Modern manufacturing environments continuously generate operational alerts from connected machines and monitoring systems.

For example, one degrading machine may simultaneously produce:

* High temperature
* High vibration
* Abnormal RPM
* Predictive maintenance warning

When these alerts are viewed independently, operators may need to investigate each alert separately.

### The problem

```text
Multiple alerts
      ↓
Fragmented information
      ↓
Slow investigation
      ↓
Difficult root-cause identification
      ↓
Delayed response
```

### X.A.Z.E.L. approach

```text
Multiple operational signals
            ↓
      Alert correlation
            ↓
      One machine incident
            ↓
       AI investigation
            ↓
      Probable root cause
            ↓
      Production impact
            ↓
         Priority
            ↓
       Remediation
            ↓
     Human approval
            ↓
    Safe execution
            ↓
       Verification
            ↓
         Audit
```

---

# 🏭 Target Industry

## Smart Manufacturing

The current implementation is specifically focused on:

* Manufacturing plants
* Production lines
* Connected industrial machinery
* Machine-health monitoring
* Maintenance operations
* Production incident management

### Primary users

* Plant operators
* Maintenance teams
* Operations teams
* Production managers

---

# 🚨 Core Use Case

### Machine M-101 — Assembly Line A

The primary demonstration models a production machine that develops a **probable mechanical degradation pattern**.

Example simulated condition:

```text
Temperature  → 93 °C
Vibration    → 1.02
RPM          → abnormal
Maintenance  → elevated risk
```

X.A.Z.E.L. recognizes that these signals may represent the same underlying incident.

Instead of producing four unrelated alerts:

```text
Temperature Alert
Vibration Alert
RPM Alert
Maintenance Alert
```

the system produces:

```text
4 RELATED ALERTS
        ↓
1 MACHINE INCIDENT
```

---

# 🧠 What X.A.Z.E.L. Does

X.A.Z.E.L. follows an incident-resolution workflow:

```text
1. Detection
2. Correlation
3. Incident Creation
4. Investigation
5. Root Cause Analysis
6. Impact Assessment
7. Prioritization
8. Remediation Planning
9. Policy Check
10. Human Approval
11. Safe Simulated Execution
12. Verification
13. Resolution
14. Audit
```

The goal is to go beyond simply displaying or classifying alerts and demonstrate an actionable incident workflow.

---

# 📊 Machine Parameters

The primary simulated machine-health parameters are:

| Parameter       | Purpose                                  |
| --------------- | ---------------------------------------- |
| Temperature     | Detect abnormal heating                  |
| Vibration       | Identify possible mechanical instability |
| RPM             | Identify operating-speed deviation       |
| Pressure        | Monitor operating conditions             |
| Humidity        | Provide environmental context            |
| Battery / Power | Monitor device or energy condition       |

Additional contextual parameters include:

* Machine ID
* Machine type
* Plant
* Production line
* Machine criticality
* Timestamp
* Alert severity
* Maintenance risk
* Production impact
* Incident priority
* Approval status
* Verification status

### Important

The current prototype uses **simulated telemetry** because physical industrial hardware is not required for the software demonstration.

The telemetry generator is a replaceable data source. In a real deployment, it could be replaced by a sensor/PLC/IoT ingestion layer while keeping the downstream intelligence and incident-resolution workflow.

---

# 🔗 Alert Correlation

Correlation is a core part of the solution.

X.A.Z.E.L. evaluates multiple operational signals using contextual information such as:

* Machine identity
* Time context
* Signal relationships
* Operational state
* Maintenance evidence

Example:

```text
High Temperature
       +
High Vibration
       +
RPM Deviation
       +
Maintenance Risk
       ↓
Correlation Engine
       ↓
ONE MACHINE INCIDENT
```

This allows the system to reason about the **incident**, rather than treating every alert as an independent event.

---

# 🤖 AI Investigation

The AI reasoning layer uses the correlated incident context to:

* Investigate available evidence
* Explain relationships between signals
* Identify a probable root cause
* Explain production impact
* Recommend remediation
* Generate human-readable incident explanations

Example:

```text
Probable Root Cause:
Mechanical degradation / possible bearing-related issue

Evidence:
- Temperature increased
- Vibration increased
- RPM deviated
- Maintenance risk increased
- Signals belong to the same machine context
```

AI-generated conclusions are expressed as **probable findings**, not absolute physical diagnoses.

---

# 📈 Production Impact & Priority

X.A.Z.E.L. adds manufacturing context to technical alerts.

Example:

```text
Machine:
M-101

Production Line:
Assembly Line A

Machine Criticality:
HIGH

Current Machine Risk:
HIGH

Potential Production Impact:
HIGH
```

These factors contribute to incident prioritization.

The system therefore moves from:

```text
"Temperature is high"
```

to:

```text
"Multiple machine signals indicate a potentially significant
incident affecting a high-criticality production machine."
```

---

# 🔧 Remediation

For the primary demonstration, X.A.Z.E.L. recommends an appropriate response such as:

> **Isolate M-101 and initiate maintenance inspection.**

The prototype intentionally separates AI reasoning from direct industrial control.

### Human approval

For actions requiring intervention:

```text
X.A.Z.E.L. Recommendation
        ↓
Approval Required
        ↓
Authorized Operator
        ↓
Approve
        ↓
Safe Simulated Execution
        ↓
Verification
```

No real industrial machine is automatically controlled by the prototype.

---

# ✅ Verification & Audit

After the simulated remediation:

```text
Execution
   ↓
Post-action machine state
   ↓
Verification
   ↓
Incident Resolution
```

The incident lifecycle is auditable through recorded state transitions such as:

```text
Detection
Correlation
Investigation
RCA
Impact Assessment
Priority
Remediation
Approval
Execution
Verification
Resolution
```

---

# 🏗️ Architecture

```text
                    X.A.Z.E.L.
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Telemetry          Vision         Operations
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                Alert Normalization
                         ↓
                 Alert Correlation
                         ↓
                   Incident Engine
                         ↓
              ┌──────────┼───────────┐
              ↓          ↓           ↓
         Investigation   RCA       Impact
              │          │           │
              └──────────┼───────────┘
                         ↓
                     Priority
                         ↓
                   Remediation
                         ↓
                 Policy / Approval
                         ↓
                   Execution
                         ↓
                   Verification
                         ↓
                     Audit
                         ↓
                  Command Center
```

---

# 🛠️ Technical Stack

## Frontend

* React.js
* Vite
* Tailwind CSS
* CSS
* Recharts

## Backend

* Python
* FastAPI
* Pydantic
* WebSockets

## AI

* Groq
* AI reasoning for investigation and recommendations

## Machine Learning

* scikit-learn
* Predictive-maintenance / machine-health analysis

## Computer Vision

* OpenCV
* Optional visual evidence processing

## Security

* JWT authentication
* Role-Based Access Control (RBAC)
* Rate limiting
* Audit logging

## Development & Deployment

* Git
* GitHub
* Render

---

# 🧮 Intelligence & Decision Logic

The system combines deterministic processing with AI reasoning.

### Deterministic components

Used for:

* Data validation
* Threshold detection
* Alert generation
* Alert correlation
* Risk evaluation
* Incident state transitions
* Authorization
* Approval requirements
* Verification workflow

### AI components

Used for:

* Investigation
* Contextual reasoning
* Root-cause explanation
* Impact explanation
* Remediation recommendations
* Natural-language responses

This separation allows AI reasoning to work together with explicit policy and safety boundaries.

---

# 📡 Telemetry Flow

The current prototype uses simulated telemetry.

```text
Python Telemetry Generator
          ↓
Telemetry Model
          ↓
Validation
          ↓
Anomaly Detection
          ↓
Alert Generation
          ↓
WebSocket Stream
          ↓
React Dashboard
```

In a real manufacturing deployment:

```text
Industrial Sensors / PLC / IoT Gateway
                ↓
          Data Ingestion
                ↓
       Pydantic Validation
                ↓
        X.A.Z.E.L. Pipeline
```

Pydantic acts as the **data contract and validation layer**. It does not collect the physical sensor data.

---

# 🖥️ Dashboard

The X.A.Z.E.L. command center provides visibility into:

* Machine health
* Live telemetry
* Correlated alerts
* Active incidents
* AI investigation
* Production impact
* Remediation
* Human approval
* Verification
* Safety monitoring
* Energy information
* Predictive maintenance
* Audit history
* Voice/text interaction

The primary dashboard is designed to tell one clear story:

```text
Machine
   ↓
Abnormal Signals
   ↓
Multiple Alerts
   ↓
Correlation
   ↓
One Incident
   ↓
AI Investigation
   ↓
Root Cause
   ↓
Impact
   ↓
Priority
   ↓
Remediation
   ↓
Approval
   ↓
Execution
   ↓
Verification
   ↓
Resolved
```

---

# 🎬 Demo Scenario

## Manufacturing Machine Incident

### Step 1 — Normal operation

```text
Machine: M-101
Production Line: Assembly Line A

Temperature: 72 °C
Vibration: 0.30
RPM: 1800
```

### Step 2 — Machine degradation

```text
Temperature: 93 °C
Vibration: 1.02
RPM: abnormal
Maintenance Risk: Elevated
```

### Step 3 — Alert generation

```text
High Temperature
High Vibration
RPM Deviation
Maintenance Warning
```

### Step 4 — Correlation

```text
4 related alerts
       ↓
1 machine incident
```

### Step 5 — AI investigation

```text
Probable Cause:
Mechanical degradation
```

### Step 6 — Impact

```text
Potential production interruption
on Assembly Line A
```

### Step 7 — Remediation

```text
Recommended:
Isolate M-101 and initiate maintenance inspection
```

### Step 8 — Approval

```text
Human approval required
```

### Step 9 — Execution

```text
Safe simulated machine isolation
```

### Step 10 — Verification

```text
Post-action state checked
        ↓
Incident resolved
```

---

# 🚀 Getting Started

## Prerequisites

Install:

* Python 3.12
* Node.js
* npm
* Git

---

## Backend Setup

From the project root:

```bash
python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the provided example configuration.

Configure the required environment variables, including the Groq API key and authentication configuration used by the project.

Start the backend:

```bash
python -m uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🎨 Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will provide the local frontend URL.

The frontend uses environment-based API/WebSocket configuration.

---

# 🔑 Environment Variables

Do not commit secrets.

Typical configuration includes:

```text
GROQ_API_KEY=
JWT_SECRET=
DEMO_MODE=
VITE_API_BASE_URL=
VITE_WS_BASE_URL=
```

Use the project's `.env.example` files as the source of truth for currently supported variables.

---

# 🔌 Key APIs

Existing APIs include functionality for:

### Health

```text
GET /health
```

### AI Agent

```text
POST /agent/analyze
```

### Telemetry

```text
GET /telemetry/latest
GET /telemetry/status
WebSocket /ws/telemetry
```

### Incidents

```text
GET /incidents
GET /incidents/{incident_id}
POST /incidents/detect
POST /incidents/run-resolution
```

Additional incident investigation, approval, remediation and verification endpoints are available through the API documentation.

---

# 🧪 Testing

Backend:

```bash
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Additional validation:

```bash
python -m compileall backend
```

---

# 🔐 Security & Safety

X.A.Z.E.L. is designed with explicit safety boundaries.

The prototype does **not**:

* Perform facial identification
* Create biometric identity profiles
* Diagnose medical conditions
* Contact emergency services
* Execute real financial transactions
* Generate malware
* Perform credential theft
* Perform unauthorized system access
* Execute arbitrary shell commands
* Automatically control physical industrial equipment

Sensitive operational actions use authorization and human approval.

---

# 👤 Human Safety Monitoring

The project also includes a simulated human safety layer for manufacturing environments.

It can monitor simulated/general signals such as:

* Operator presence
* Activity level
* Inactivity duration
* Environmental risk
* Possible proximity risk
* Fatigue-related patterns
* Emergency/SOS state

The safety module provides:

```text
Observation
+
Risk Assessment
+
Recommended Action
```

It is **not a medical diagnostic system**.

---

# ⚡ Predictive Maintenance & Energy Intelligence

X.A.Z.E.L. also incorporates supporting operational intelligence.

### Predictive Maintenance

Provides evidence such as:

* Machine health
* Failure risk
* Degradation trends
* Maintenance recommendations

### Energy Intelligence

Provides supporting information such as:

* Power demand
* Solar generation
* Energy efficiency
* Energy alerts
* Optimization information

These modules are treated as **operational evidence sources** that can support incident investigation and impact analysis.

---

# 🎯 Why Manufacturing?

Manufacturing provides a clear environment in which:

* machine telemetry
* maintenance signals
* operational alerts
* safety information
* production impact

can intersect within the same incident.

This makes the AI-01 incident-resolution lifecycle demonstrable in a concrete industrial scenario.

---

# 📌 Example Reviewer Explanation

> **X.A.Z.E.L. is an AI-powered autonomous incident-resolution platform for smart manufacturing. A production machine can generate multiple alerts such as high temperature, abnormal vibration, RPM deviation and maintenance risk. Instead of treating those alerts independently, X.A.Z.E.L. correlates them into a single incident, investigates the available evidence using AI reasoning, identifies a probable root cause, assesses production impact, prioritizes the incident and recommends remediation. Actions requiring intervention are routed through authorization and human approval, followed by safe simulated execution, verification and audit.**

---

# ⚠️ Current Prototype Limitations

This repository contains a hackathon prototype.

Current limitations include:

* Machine telemetry is simulated.
* Safety signals are simulated.
* Remediation execution is simulated.
* Verification is simulated.
* Some incident/audit state may be maintained in memory.
* Machine thresholds are configurable prototype values, not universal industrial standards.
* No physical PLC/industrial machine is directly controlled.
* Production deployment requires integration with appropriate industrial data-acquisition infrastructure.

---

# 🔮 Future Scope

Possible future extensions include:

* Real industrial sensor integration
* PLC / OPC UA / MQTT data ingestion
* Persistent incident history
* Plant-wide multi-machine support
* More advanced anomaly detection
* Digital-twin integration
* Maintenance-management integration
* Production scheduling integration
* Additional manufacturing incident types
* Enterprise observability integrations
* More sophisticated causal analysis

---

# 📁 High-Level Project Structure

```text
X.A.Z.E.L.
│
├── backend/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
├── data/
│   ├── generator.py
│   └── safety_generator.py
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       └── services/
│
├── docs/
│   └── MANUFACTURING_DEMO.md
│
├── tests/
│   └── test_incidents.py
│
├── requirements.txt
├── runtime.txt
└── README.md
```

---

# 🏆 Project Evolution

```text
THINK
AI Agent
   ↓
SENSE
Real-Time Telemetry
   ↓
SEE
Command Center
   ↓
PREDICT
Predictive Maintenance
   ↓
OPTIMIZE
Energy Intelligence
   ↓
PROTECT
Safety Intelligence
   ↓
RESOLVE
Autonomous Incident Resolution
```

---

# 📄 Problem Statement Alignment

X.A.Z.E.L. is specialized toward **AI-01 — Autonomous Enterprise Incident Resolution Engine**.

The implementation addresses the core AI-01 workflow through:

| AI-01 Requirement                      | X.A.Z.E.L. Implementation                          |
| -------------------------------------- | -------------------------------------------------- |
| Heterogeneous operational alerts       | Telemetry, maintenance and operational signals     |
| Alert correlation                      | Multi-signal correlation engine                    |
| Probable root cause                    | AI investigation + RCA                             |
| Severity / impact prioritization       | Risk and incident priority logic                   |
| Remediation recommendation             | Remediation service                                |
| Autonomous execution where appropriate | Safe simulated execution                           |
| Human approval                         | Authentication / authorization / approval workflow |
| Auditability                           | Incident and audit records                         |
| End-to-end workflow                    | Detection → Resolution → Verification              |

---

# 👩‍💻 Project Status

**Prototype Status:** Functional Hackathon Prototype

**Primary Domain:** Smart Manufacturing

**Primary Use Case:** Machine Incident Resolution

**Core Intelligence:** AI-assisted investigation + deterministic operational workflow

**Deployment Model:** Web application with FastAPI backend and React frontend

---

## License

Add the project's license here if one is selected.

---

## Team

Built as a hackathon project for **IGNITRRON'26**.

# X.A.Z.E.L.

### Detect. Correlate. Investigate. Resolve.
