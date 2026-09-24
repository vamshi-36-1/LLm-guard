# Proxy integration

`middleware.py` is an adapter that Person 1 can import from the team's existing proxy. It keeps the DLP service separate so the existing reverse-proxy implementation is not overwritten.

Recommended flow:
1. Receive application prompt.
2. `DLPClient.redact_input(prompt)`.
3. Send sanitized prompt upstream.
4. Validate LLM response with `validate_output`.
5. Block/redact according to the team's proxy policy.
6. Preserve DLP audit events.
