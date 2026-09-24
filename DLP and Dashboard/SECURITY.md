# Security notes

- Do not commit production API keys, passwords, tokens, or PII.
- Replace development secrets with a managed secret store.
- Protect the DLP API with authentication/authorization before production exposure.
- Treat audit logs as sensitive data.
- Review allowlist changes through change control.
- Choose fail-open/fail-closed behavior at the proxy layer based on the team's security policy.
