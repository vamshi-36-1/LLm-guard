"""
LLM-Guard Proxy - Production Operations Runbook
Operational procedures for production deployment
"""

# ============================================
# DEPLOYMENT
# ============================================

## Starting Proxy

### Using Docker
```bash
docker build -t llm-guard-proxy:latest .
docker run -p 8888:8888 llm-guard-proxy:latest
```

### Using Docker Compose (Recommended)
```bash
docker-compose up -d
docker-compose logs -f proxy
```

### Manual
```bash
pip install -r requirements.txt
python main_week3.py
```

## Verifying Deployment

```bash
# Health check
curl http://localhost:8888/

# Metrics
curl http://localhost:8888/metrics/summary

# Detailed health
curl http://localhost:8888/health/detailed
```

---

# ============================================
# MONITORING & ALERTS
# ============================================

## Accessing Dashboards

- **Grafana (Dashboards):** http://localhost:3000
- **Prometheus (Metrics):** http://localhost:9090
- **AlertManager:** http://localhost:9093

## Common Alerts & Resolution

### 🚨 CRITICAL: Proxy Down

**Symptoms:**
- Alert: "ProxyDown"
- Status code 0, connection refused

**Resolution:**
1. Check proxy logs: `docker-compose logs proxy`
2. Check resource usage: `docker stats proxy`
3. Restart: `docker-compose restart proxy`
4. Check dependencies: Are detector models present?
5. Review recent changes in git log

**Prevention:**
- Monitor uptime with: `curl http://localhost:8888/`
- Set up automatic restart: `restart_policy.condition: on-failure`

### 🚨 CRITICAL: High Error Rate (>5%)

**Symptoms:**
- Alert: "HighErrorRate"
- Metrics show >5% error rate for 2+ minutes

**Resolution:**
1. Check logs: `docker-compose logs proxy | grep ERROR`
2. Check upstream: Is LLM API responding?
3. Check detector: Are models loaded correctly?
4. Check rate limiter: Circuit breaker state?
   ```bash
   curl http://localhost:8888/health/detailed | grep circuit_breaker
   ```
5. Restart if needed: `docker-compose restart proxy`

**Causes:**
- Upstream API down
- Detector model missing
- Circuit breaker open
- Resource exhaustion

### 🚨 CRITICAL: High Latency (P99 >100ms)

**Symptoms:**
- Alert: "HighLatency"
- /metrics shows p99_ms >100

**Resolution:**
1. Check resource usage:
   ```bash
   docker stats proxy
   ```
2. Check queue depth:
   ```bash
   curl http://localhost:8888/metrics/summary | grep queue
   ```
3. Check detector latency:
   ```bash
   curl http://localhost:8888/health/detailed | grep jailbreak_detection
   ```
4. Scale up if needed:
   - Increase replicas in docker-compose
   - Add load balancer

**Causes:**
- High traffic volume
- Detector model slow
- Upstream slow
- Resource constrained

### ⚠️ WARNING: Circuit Breaker Open

**Symptoms:**
- Alert: "CircuitBreakerOpen"
- Health shows state: OPEN

**Resolution:**
1. Check upstream status:
   ```bash
   curl https://api.openai.com/v1/chat/completions -v
   ```
2. Check error rate:
   ```bash
   curl http://localhost:8888/metrics | grep error_rate
   ```
3. Wait 60s for automatic recovery (circuit breaker auto-recovers)
4. Or manually restart upstream connection:
   ```bash
   docker-compose restart proxy
   ```

**Note:** Circuit breaker will transition to HALF_OPEN after 60s, then CLOSED if requests succeed

### ⚠️ WARNING: Rate Limiting Active

**Symptoms:**
- Alert: "HighRateLimited"
- Many 429 responses

**Resolution:**
1. Check rate limit settings in main_week3.py:
   ```python
   rate_limiter = RateLimitingManager(
       global_rate=10.0,      # Increase if needed
       per_user_rate=5.0
   )
   ```
2. Check user IDs making requests:
   ```bash
   docker-compose logs proxy | grep rate_limited
   ```
3. Whitelist high-volume users or increase limits
4. Restart: `docker-compose restart proxy`

---

# ============================================
# TROUBLESHOOTING
# ============================================

## Proxy Won't Start

**Check:**
1. Port 8888 already in use:
   ```bash
   lsof -i :8888
   # Kill if needed: kill -9 <PID>
   ```

2. Dependencies missing:
   ```bash
   pip install -r requirements.txt
   ```

3. Model files missing:
   ```bash
   ls -la models/
   ls -la jailbreak_patterns.json
   ```

4. Python version:
   ```bash
   python --version  # Should be 3.8+
   ```

## High Memory Usage

**Check:**
```bash
docker stats proxy
```

**If >500MB:**
1. Check for memory leaks in logs
2. Restart: `docker-compose restart proxy`
3. Check cache sizes (if Redis enabled)
4. Review load test results

## Connection Timeout to Upstream

**Check:**
1. Upstream URL in main_week3.py
2. Network connectivity: `curl https://your-upstream-url`
3. Firewall rules
4. DNS resolution: `nslookup your-upstream-url`

## Detector Not Detecting Jailbreaks

**Check:**
1. Model files exist:
   ```bash
   ls -la models/jailbreak_svm_v1.pkl
   ```

2. Test detector directly:
   ```bash
   python
   from hybrid_detector import HybridDetector
   detector = HybridDetector(...)
   result = detector.detect("Ignore all instructions")
   ```

3. Check logs for detector errors:
   ```bash
   docker-compose logs proxy | grep detector
   ```

---

# ============================================
# MAINTENANCE
# ============================================

## Regular Tasks

### Daily
- Check dashboards: http://localhost:3000
- Review alerts in AlertManager
- Check error logs: `docker-compose logs proxy | grep ERROR`

### Weekly
- Run load test: `python deployment_automation_week4.py`
- Review performance metrics
- Check for security updates in dependencies

### Monthly
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Review deployment history
- Capacity planning for next month
- Backup configurations

## Backup & Restore

### Backup
```bash
docker-compose exec proxy tar czf /backups/proxy-backup-$(date +%Y%m%d).tar.gz .
```

### Restore
```bash
docker-compose exec proxy tar xzf /backups/proxy-backup-20240101.tar.gz
docker-compose restart proxy
```

## Updating Proxy

### 1. Test in staging
```bash
docker-compose -f docker-compose.staging.yml up -d
# Run tests
```

### 2. Backup production
```bash
docker-compose exec proxy tar czf /backups/backup-pre-update.tar.gz .
```

### 3. Graceful shutdown
```bash
docker-compose exec proxy kill -TERM 1
```

### 4. Deploy new version
```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### 5. Verify
```bash
curl http://localhost:8888/health/detailed
```

## Rollback Procedure

```bash
# Stop current version
docker-compose down

# Restore backup
tar xzf /backups/backup-pre-update.tar.gz

# Start old version
docker-compose up -d

# Verify
curl http://localhost:8888/
```

---

# ============================================
# PERFORMANCE TUNING
# ============================================

## Increasing Throughput

### 1. Horizontal scaling
```yaml
# In docker-compose.yml
services:
  proxy:
    deploy:
      replicas: 3
```

### 2. Increase rate limits
```python
rate_limiter = RateLimitingManager(
    global_rate=100.0,    # Increase from 10
    per_user_rate=50.0    # Increase from 5
)
```

### 3. Add connection pooling
```python
httpx.AsyncClient(
    pool_limits=httpx.PoolLimits(
        max_connections=100,
        max_keepalive_connections=20
    )
)
```

## Reducing Latency

### 1. Enable caching
- Uncomment Redis in docker-compose.yml
- Implement request caching for repeated prompts

### 2. Connection reuse
- Already enabled in httpx.AsyncClient()

### 3. Optimize detector
- Use lighter embedding model if available
- Cache embeddings for common patterns

---

# ============================================
# EMERGENCY PROCEDURES
# ============================================

## Complete Service Failure

```bash
# 1. Kill everything
docker-compose down -v

# 2. Clean up
rm -rf backups/* logs/*

# 3. Restore from backup
tar xzf /backups/latest-backup.tar.gz

# 4. Restart
docker-compose up -d

# 5. Verify
curl http://localhost:8888/
```

## Data Corruption Recovery

```bash
# 1. Backup corrupted data
cp -r data data.corrupt

# 2. Restore from backups/
cp backups/data.backup/* data/

# 3. Restart services
docker-compose restart proxy

# 4. Verify health
curl http://localhost:8888/health/detailed
```

---

# ============================================
# CONTACTS & ESCALATION
# ============================================

**On-Call Engineer:** [Contact info]  
**Backend Lead:** Person 1  
**Security Lead:** Person 2  
**Slack Channel:** #llm-guard-alerts

**Escalation Path:**
1. Try resolution steps above
2. Contact on-call engineer
3. Page backend lead if critical
4. All-hands if service completely down

---

**Last Updated:** Week 4  
**Version:** 1.0  
**Status:** Production Ready
