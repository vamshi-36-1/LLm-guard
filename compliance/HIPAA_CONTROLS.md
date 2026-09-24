# HIPAA-oriented DLP controls

This document maps the Person 3 implementation to operational controls relevant to protecting ePHI. It is **not a legal certification or claim of HIPAA compliance**. A covered entity/business associate must perform its own risk analysis and compliance review.

| Control area | Implementation evidence | Operational requirement |
|---|---|---|
| Minimum necessary | Input/output DLP validation | Configure entity policies and only transmit required data |
| Access control | Service boundary + deployment controls | Restrict DLP/API access with the team's identity layer |
| Audit controls | JSONL audit logger | Protect, rotate, retain, and review logs according to policy |
| Integrity | Structured events + validation | Centralize logs and protect from unauthorized modification |
| Transmission security | HTTPS/TLS at deployment layer | Terminate TLS and require encrypted service-to-service traffic |
| Incident response | Audit events + blocked entity metadata | Integrate alerts with incident procedures |

No raw secret values are intentionally written to the audit event fields. Review production logging and retention before deployment.
