# LLM-Guard Person 4 Production Runbook

## Deploy
1. Build DLP image and dashboard image.
2. Configure secrets outside source control (`DLP_TOKEN_SECRET`, TLS, auth).
3. Start services with Docker Compose or deploy dashboard to Netlify/Vercel.
4. Configure Prometheus to scrape `/metrics`.
5. Configure alert routing in the organization's monitoring stack.

## Health checks
- DLP: `/health`
- Metrics: `/metrics`
- Dashboard: `/`
- WebSocket: `/ws/events`

## Incident response
1. Check dashboard alerts.
2. Inspect DLP audit events without exposing raw PII/secrets.
3. Verify upstream proxy health.
4. If DLP is unavailable, follow the team's fail-open/fail-closed security policy; do not invent a default.
5. Preserve relevant logs and timestamps.

## Rollback
Deploy the previously approved container/image or previous frontend release. Verify health checks before reopening traffic.

## Backups/recovery
Audit logs must be stored in the team's approved durable logging system; the default local JSONL file is only a development implementation.
