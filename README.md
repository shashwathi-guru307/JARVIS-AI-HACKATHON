# J.A.R.V.I.S.

## AI-Powered Autonomous Incident Resolution for Smart Manufacturing

J.A.R.V.I.S. is a prototype manufacturing operations command center for plant operators, maintenance teams, and operations managers. It turns multiple machine alerts into one explainable incident workflow instead of treating every alert as an unrelated failure.

## Problem and Target Industry

Smart manufacturing plants contain connected production machines that emit temperature, vibration, RPM, and predictive-maintenance alerts. Several alerts can describe one underlying mechanical condition. J.A.R.V.I.S. correlates those signals, investigates the evidence, assesses production impact, prioritizes the incident, recommends remediation, obtains approval, verifies the safe simulation, and records the audit trail.

The target industry is smart manufacturing, specifically production plants with connected industrial machinery. The demo context is Smart Manufacturing Plant, Assembly Line A, machine M-101. Primary users are plant operators, maintenance teams, and operations managers.

## Parameters

The six visible machine-health parameters are:

| Parameter | Unit | Use |
|---|---|---|
| Temperature | °C | Thermal stress signal |
| Vibration | Configurable level | Mechanical stress signal |
| RPM | Revolutions per minute | Operating-speed deviation |
| Pressure | Configurable operating pressure | Process context |
| Humidity | % | Environmental context |
| Battery/Power | % | Machine power context |

The system also uses machine identity, criticality, alert severity, maintenance risk, production impact, approval status, execution status, verification status, and audit status. Thresholds are configurable prototype demo thresholds, not universal industrial standards. Example rules currently include temperature warning/critical values of 85/95, vibration warning/critical values of 0.60/0.90, and battery warning/critical values of 30/10.

## Architecture

```text
Machine Signals
  -> Alert Normalization
  -> Deterministic Correlation
  -> One Machine Incident
  -> AI Investigation / Root Cause Explanation
  -> Production Impact
  -> Priority
  -> Remediation Plan
  -> Human Approval
  -> Safe Simulated Execution
  -> Verification
  -> Resolution and Audit
```

Deterministic services control telemetry validation, threshold detection, correlation, incident lifecycle, authorization, safe-action policy, verification state, and audit transitions. Groq is optional reasoning support for operator-facing explanations; core incident state does not depend on the LLM.

## Demo Scenario

Click **RUN MANUFACTURING INCIDENT** in the authenticated dashboard. The deterministic scenario primes simulated telemetry for M-101:

- Temperature around 94 °C
- Vibration around 0.85 g
- RPM around 2300
- Predictive maintenance degradation evidence

These are configurable simulated manufacturing values. J.A.R.V.I.S. presents them as four related signals for one probable mechanical degradation / possible bearing-related incident on Assembly Line A. The workflow stops at human approval, then performs a safe simulated load reduction, primes a recovery state, verifies improvement, and records audit transitions. No real machine is controlled.

## AI Responsibilities

The AI/Groq layer can provide investigation narratives, evidence interpretation, contextual reasoning, probable-root-cause explanations, impact explanations, remediation recommendations, and conversational summaries. It does not control industrial equipment, execute shell commands, or bypass approval. Deterministic rules and policy controls remain authoritative.

## Technology Stack

Python, FastAPI, Pydantic, React, Vite, Tailwind CSS, WebSockets, Groq integration, OpenCV/vision services, and the existing predictive-maintenance model.

## Local Development

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, authenticate as a configured demo operator/admin, and click **RUN MANUFACTURING INCIDENT**. API docs are available at `http://localhost:8000/docs`.

Useful endpoints include `/health`, `/system/status`, `/manufacturing/plant`, `/incidents`, `/incidents/run-resolution`, and `/agent/analyze`.

## Security and Safety

JWT authentication, RBAC, rate limiting, and audit logging are preserved. Approval and execution require an authenticated operator or admin. Remediation is explicitly simulated: there is no shell execution, physical machine control, financial action, credential change, or emergency dispatch.

## Deployment

The existing Render architecture is preserved:

- Backend root: repository root
- Backend build: `pip install -r requirements.txt`
- Backend start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Frontend root: `frontend`
- Frontend build: `npm install && npm run build`
- Frontend publish directory: `dist`

Configure `GROQ_API_KEY`, `GROQ_MODEL`, `JWT_SECRET`, `CORS_ORIGINS`, `DEMO_MODE`, demo passwords, `VITE_API_BASE_URL`, and `VITE_WS_BASE_URL` through deployment environment variables. Use HTTPS and WSS production URLs. No deployment was claimed or changed by this implementation.

## Limitations

- Incident and audit state are bounded in-memory prototype state.
- Telemetry and remediation are simulated for the hackathon demo.
- Thresholds are configurable examples, not plant-wide standards.
- Verification demonstrates workflow state improvement and does not certify physical equipment safety.

## Reviewer FAQ

**Which industry are you targeting?** Smart manufacturing, specifically production plants with connected industrial machinery.

**What parameters are you using?** Temperature, vibration, RPM, pressure, humidity, battery/power, plus machine metadata, alert severity, maintenance risk, and production impact.

**What problem are you solving?** Multiple manufacturing alerts may represent one underlying machine failure. J.A.R.V.I.S. correlates those signals into one incident and manages investigation through resolution.

**Where is the AI?** AI explains correlated evidence, probable cause, impact, and remediation. Deterministic rules and policy controls govern detection, authorization, and safe execution.

**Is it controlling an industrial machine?** No. The current prototype performs safe simulated remediation only.

**Why manufacturing?** Machine telemetry, maintenance evidence, and production impact naturally intersect, making incident correlation and resolution demonstrable.

See [docs/MANUFACTURING_DEMO.md](docs/MANUFACTURING_DEMO.md) for the reviewer walkthrough.
