# GDPR-oriented DLP controls

This document maps implementation features to operational privacy controls. It is **not legal advice or a certification of GDPR compliance**.

| Control area | Implementation evidence | Operational requirement |
|---|---|---|
| Data minimisation | Input redaction | Configure only required entity detection and retention |
| Privacy by design | PII masking before upstream calls | Keep protected values out of unnecessary systems |
| Accountability | Audit log | Define ownership, retention, access and review procedures |
| Security of processing | API boundary, Docker deployment | Apply authentication, TLS, secrets management and network controls |
| Rights/retention | Audit path is configurable | Define deletion/retention schedules with legal/privacy owners |
| Incident response | Validation/block events | Feed security events into the team's incident workflow |
