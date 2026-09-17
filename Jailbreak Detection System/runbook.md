# Operations Runbook

## Quick Status Check
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### High Latency (>50ms)
1. Check CPU usage
2. Check cache hit rate
3. Restart detector service

### High Error Rate
1. Check logs
2. Check disk space
3. Verify model files

### Accuracy Degraded
1. Check model version
2. Review recent examples
3. Rollback if needed

## Rollback Procedure
```bash
git checkout previous_version
# Restart detector
```