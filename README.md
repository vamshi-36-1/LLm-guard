# LLM-Guard — Person 3 + Person 4 Complete Work Package

This repository contains the Person 3 (DLP Engineer) and Person 4 (Frontend/DevOps Lead) implementation mapped to the 4-week LLM-Guard workplan. It is designed to be copied into the team's existing `LLm-guard` monorepo without replacing Person 1 or Person 2 code.

## Scope mapped to the workplan

### Person 3 — DLP Engineer
- Week 1: Presidio/NER setup, API-key recognizer, input redaction, custom entities, masking, <50 ms benchmark harness.
- Week 2: output leakage validation, allowlist manager, JSONL audit log, false-positive evaluation harness.
- Week 3: proxy integration adapter, input/output middleware, reversible token vault for controlled unmasking, compliance documentation.
- Week 4: integration tests, HIPAA/GDPR operational-control documents, benchmark runner, production-readiness checklist.

### Person 4 — Frontend/DevOps Lead
- Week 1: React + TypeScript dashboard, two main tabs, mock API, WebSocket support, responsive UI.
- Week 2: API client, live WebSocket events, auto-refresh, high-severity alerts.
- Week 3: frontend unit tests, E2E tests, Prometheus metrics, GitHub Actions CI.
- Week 4: Docker/Nginx, Netlify/Vercel deployment configs, Prometheus/alerting config, runbook, Lighthouse configuration.

## Important integration note
The workplan describes a 4-person team. This package therefore contains **only Person 3 and Person 4 work**. Copy/merge it into the team's existing repository; do not delete existing Person 1/2 directories.

## Run locally

### DLP API
```bash
cd dlp
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app:app --reload --port 8001
```

### Dashboard
```bash
cd dashboard
npm install
npm run dev
```
Dashboard: http://localhost:3000
DLP API: http://localhost:8001/docs

### Docker
```bash
docker compose up --build
```

## Test

DLP:
```bash
cd dlp
pytest -q --cov=. --cov-report=term-missing --cov-fail-under=80
```

Dashboard:
```bash
cd dashboard
npm ci
npm run test:coverage
npm run build
```

## Benchmark
```bash
cd dlp
python ../benchmarks/dlp_benchmark.py --requests 200
```
The workplan target is <50 ms/request for the DLP component. Benchmark results depend on the machine, model warm-up, and installed recognizers; record actual measurements rather than claiming a target has been met without running the benchmark.

## Git workflow for the team
Create a feature branch, copy these files into the team's existing monorepo, review conflicts, commit, push, and open a pull request.

```bash
git checkout -b person3-person4
git add dlp dashboard integration compliance benchmarks prometheus .github/workflows docker-compose.yml docs
git commit -m "feat: add person 3 DLP and person 4 dashboard"
git push -u origin person3-person4
```
