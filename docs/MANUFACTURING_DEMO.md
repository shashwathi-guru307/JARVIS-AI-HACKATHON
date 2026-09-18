# X.A.Z.E.L. Smart Manufacturing Demo

## Industry and Users

X.A.Z.E.L. targets smart manufacturing plants with connected production machinery. The primary users are plant operators, maintenance teams, and operations managers.

## Parameters

The visible machine parameters are temperature, vibration, RPM, pressure, humidity, and battery/power. The incident also uses machine identity, criticality, alert severity, maintenance risk, production impact, approval, execution, verification, and audit state. Demo thresholds are configurable prototype values rather than universal industrial standards.

## Scenario

The demo represents M-101, an industrial rotating production machine on Assembly Line A in a Smart Manufacturing Plant. Its simulated temperature, vibration, RPM, and predictive-maintenance evidence form a probable mechanical degradation / possible bearing-related pattern.

## Correlation

The project does not treat each machine alert independently. It correlates multiple operational signals that occur in the same machine and operational context, allowing X.A.Z.E.L. to reason about the underlying incident rather than merely displaying alerts.

The deterministic correlation layer normalizes elevated temperature, elevated vibration, abnormal RPM, and predictive degradation into one incident with multiple source event IDs. Existing broad correlation rules remain available to the system snapshot.

## AI Role and RCA

The deterministic layer validates telemetry, detects thresholds, correlates alerts, controls lifecycle and policy, and records audit events. The AI/Groq layer is reserved for investigation narratives and operator-facing explanation. The RCA output is explicitly a probable root cause, supported by evidence such as elevated temperature, elevated vibration, RPM deviation, and maintenance risk. It is not presented as a confirmed physical diagnosis.

## Impact and Priority

The impact engine describes potential production interruption on Assembly Line A and elevated operational safety concern using qualitative categories. Incident priority combines severity, risk score, correlated signal count, affected components, urgency, and machine criticality context.

## Remediation, Approval, and Verification

The recommended remediation is a safe simulated reduction of machine load while maintenance review is performed. Approval is required from an authenticated operator or admin. Execution cannot proceed without approval and cannot perform physical control. Execution primes a recovery simulation, after which verification records before/after simulated state and marks the incident resolved when improvement is detected.

## Audit

The bounded in-memory audit log records detection, correlation, investigation, RCA, impact assessment, remediation proposal, approval request, approval or rejection, simulated execution, verification, and resolution. No secrets, tokens, passwords, or API keys are logged.

## Demo Steps

1. Start the backend and frontend and authenticate as an operator or admin.
2. Confirm the dashboard shows Smart Manufacturing Plant, Assembly Line A, and M-101.
3. Click **RUN MANUFACTURING INCIDENT**.
4. Review the four related signals and one machine incident.
5. Review probable root cause, evidence, production impact, priority, and remediation.
6. Approve remediation using the authenticated control, or reject it to demonstrate the policy boundary.
7. Execute the safe simulation and verify the recovery state.
8. Confirm `RESOLVED` and inspect the audit trail.

## Reviewer Questions

**Which industry are you targeting?** Smart manufacturing, specifically production plants with connected industrial machinery.

**What parameters are you using?** Temperature, vibration, RPM, pressure, humidity, and battery/power, plus machine metadata, alert severity, maintenance risk, and production impact.

**What problem are you solving?** Manufacturing machines can generate multiple alerts for one underlying failure. We correlate those signals into a single incident and manage the investigation-to-resolution workflow.

**Where is the AI?** The AI reasoning layer investigates correlated evidence, explains probable root cause, assesses the situation, and recommends remediation. Deterministic rules and policy controls govern detection, authorization, and safe execution.

**What happens after detection?** X.A.Z.E.L. correlates alerts, investigates evidence, identifies a probable cause, assesses production impact, prioritizes, recommends remediation, obtains approval, performs a safe simulated action, verifies the result, and records the audit trail.

**Is it actually controlling an industrial machine?** No. The prototype uses safe simulated remediation and intentionally separates AI reasoning from physical control.

**Why manufacturing?** Manufacturing provides a clear environment where machine telemetry, maintenance alerts, and production impact naturally intersect.
