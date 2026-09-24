from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_email_redaction():
    r = client.post("/v1/dlp/redact", json={"text":"Contact alice@example.com", "source":"input"})
    assert r.status_code == 200
    assert "alice@example.com" not in r.json()["redacted_text"]

def test_api_key_redaction():
    r = client.post("/v1/dlp/redact", json={"text":"I like apples and bananas sk-abcdefghijklmnopqrstuvwxyz123456", "source":"input"})
    assert r.status_code == 200
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in r.json()["redacted_text"]

def test_allowlist_lifecycle():
    client.post("/v1/dlp/allowlist", json={"entity_types":["EMAIL_ADDRESS"]})
    assert "EMAIL_ADDRESS" in client.get("/v1/dlp/allowlist").json()["entity_types"]
    client.delete("/v1/dlp/allowlist/EMAIL_ADDRESS")

def test_output_validation_blocks_email_when_not_allowed():
    client.delete("/v1/dlp/allowlist/EMAIL_ADDRESS")
    r = client.post("/v1/dlp/validate", json={"text":"email alice@example.com"})
    assert r.status_code == 200
    assert r.json()["allowed"] is False

def test_metrics():
    assert client.get("/metrics").status_code == 200
