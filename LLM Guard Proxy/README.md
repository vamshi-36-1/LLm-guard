# LLM-Guard Proxy

**Project Status:** Week 1-4 ✅ Complete  
**Role:** Backend API & Security Proxy

---

## 🚀 Overview
The **LLM-Guard Proxy** is an intelligent, high-performance reverse proxy designed to intercept, analyze, and safely route traffic to upstream LLM providers (e.g., OpenAI). It acts as the first line of defense, integrating directly with the **Jailbreak Detection System** (Person 2) to block adversarial prompts in real-time before they reach the language model.

## 🛠️ Key Features

### 1. Advanced Rate Limiting & Circuit Breaking
- **Token Bucket Rate Limiter:** 10 requests/sec global limit, 5 requests/sec per-user limit.
- **Burst Handling:** Intelligent request queueing (up to 100 request buffer) to handle traffic spikes.
- **Circuit Breaker:** Automatic fault tolerance. Opens after 5 upstream failures, half-open recovery after 60s.

### 2. Monitoring & Distributed Tracing
- **Prometheus Metrics:** Tracks latency, throughput, error rates, and queue depth (`/metrics`).
- **Grafana Integration:** Visual dashboards for real-time traffic analysis.
- **Distributed Tracing:** Injects `X-Trace-ID` into every request for end-to-end observability.

### 3. Production Deployment & Security
- **Automated Deployments:** Strict pre-deployment checks (code quality, model availability, network, disk space).
- **Auto-Backups & Rollbacks:** Automatically backs up the previous state before deploying.
- **Docker Stack:** Multi-stage optimized Dockerfile and a 7-service `docker-compose.yml` (Proxy, Prometheus, Grafana, AlertManager, Redis).
- **Edge Security:** TLS/HTTPS termination via Nginx.

---

## 📁 Project Structure

```text
LLM Guard Proxy/
├── proxy.py                          # Base proxy server
├── proxy_ratelimit.py                # Proxy + Rate Limiting & Circuit Breaker
├── proxy_monitoring.py               # Optimized Proxy + Prometheus Metrics
├── rate_limiter_circuitbreaker.py    # Rate Limiting & Burst Queue logic
├── monitoring_metrics.py             # Prometheus, Latency, and Trace tracking
├── deployment_automation.py          # Pre-flight checks and automated deployment
├── load_tester.py                    # Throughput & SLA validation script
├── Dockerfile                        # Multi-stage production image
├── docker-compose.yml                # 7-service full stack configuration
├── nginx.conf                        # Reverse proxy & TLS termination
├── prometheus.yml                    # Metrics scraping config
├── alertmanager.yml                  # Alert routing
├── alert_rules.yml                   # Production alert triggers
├── SETUP_WEEK2_3.md                  # Development setup guide
└── RUNBOOK.md                        # Production operations & troubleshooting guide
```

---

## ▶️ Quick Start

### Running Locally
```powershell
# 1. Activate virtual environment
..\.venv310\Scripts\activate

# 2. Run the fully-featured Proxy
python proxy_monitoring.py
```

### Running with Docker (Production)
```bash
docker-compose up -d
```

### Endpoints
- **Proxy Endpoint:** `POST /proxy/{path}`
- **Metrics Endpoint:** `GET /metrics`
- **Health Check:** `GET /health/detailed`

---

## 📊 Performance SLAs
- **P99 Latency Goal:** < 100ms
- **Throughput:** 100 requests/sec validation
- **Uptime Target:** 99.9%
- **Error Rate Tolerance:** < 5%
