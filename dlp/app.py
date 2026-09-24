import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from config import MAX_TEXT_LENGTH
from models import *
from redactor import DLPRedactor
from allowlist import AllowlistManager
from audit import AuditLogger
from validator import OutputValidator
from token_vault import TokenVault

app = FastAPI(title="LLM-Guard DLP", version="1.0.0")
redactor = DLPRedactor()
allowlist = AllowlistManager()
audit = AuditLogger()
vault = TokenVault()
validator = OutputValidator(redactor.analyzer, allowlist)
connections: set[WebSocket] = set()
REQUESTS = Counter("dlp_requests_total", "DLP requests", ["operation", "direction"])
BLOCKS = Counter("dlp_blocks_total", "DLP blocked events", ["direction"])
LATENCY = Histogram("dlp_request_latency_seconds", "DLP request latency", ["operation"])

async def broadcast(event):
    dead = []
    for ws in connections:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.discard(ws)

def ensure_text(text):
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(413, f"text exceeds {MAX_TEXT_LENGTH} characters")

def finding_models(text, results):
    return [EntityFinding(entity_type=r.entity_type, start=r.start, end=r.end, score=float(r.score), text_preview=text[r.start:r.end][:80]) for r in results]

@app.get("/health")
def health():
    return {"status": "ok", "service": "dlp"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/v1/dlp/redact", response_model=RedactResponse)
async def redact(req: RedactRequest):
    ensure_text(req.text)
    with LATENCY.labels("redact").time():
        REQUESTS.labels("redact", req.source).inc()
        redacted, results = redactor.redact(req.text)
    findings = finding_models(req.text, results)
    event = audit.log("redaction", direction=req.source, entity_types=sorted({r.entity_type for r in results}), count=len(results))
    await broadcast(event)
    return RedactResponse(redacted_text=redacted, findings=findings)

@app.post("/v1/dlp/validate", response_model=ValidationResponse)
def validate(req: ValidationRequest):
    ensure_text(req.text)
    with LATENCY.labels("validate").time():
        REQUESTS.labels("validate", "output").inc()
        allowed, findings, blocked = validator.validate(req.text)
    if not allowed:
        BLOCKS.labels("output").inc()
    audit.log("validation", allowed=allowed, blocked_entities=blocked)
    return ValidationResponse(allowed=allowed, findings=findings, blocked_entities=blocked)

@app.post("/v1/dlp/process", response_model=RedactResponse)
async def process(req: ProcessRequest):
    ensure_text(req.text)
    if req.direction == "input":
        return await redact(RedactRequest(text=req.text, source="input", reversible=True))
    allowed, findings, blocked = validator.validate(req.text)
    if not allowed:
        BLOCKS.labels("output").inc()
    if blocked:
        redacted, results = redactor.redact(req.text)
        return RedactResponse(redacted_text=redacted, findings=findings)
    return RedactResponse(redacted_text=req.text, findings=findings)

@app.get("/v1/dlp/allowlist")
def get_allowlist():
    return {"entity_types": allowlist.list()}

@app.post("/v1/dlp/allowlist")
def add_allowlist(req: AllowlistRequest):
    return {"entity_types": allowlist.add(req.entity_types)}

@app.delete("/v1/dlp/allowlist/{entity_type}")
def delete_allowlist(entity_type: str):
    return {"entity_types": allowlist.remove(entity_type)}

@app.get("/v1/dlp/audit")
def audit_status():
    return {"audit_path": audit.path}

@app.websocket("/ws/events")
async def websocket_events(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connections.discard(ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
