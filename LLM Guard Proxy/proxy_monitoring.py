"""
LLM-Guard: Latency-Optimized Proxy with Prometheus Monitoring
Person 1 - Week 3
Integrated rate limiting, circuit breaker, and Prometheus metrics
"""

from fastapi import FastAPI, Request, Header
from fastapi.responses import Response
import httpx
import logging
from datetime import datetime
import sys
from typing import Optional
import time

# Import our components
from rate_limiter import RateLimitingManager
from monitoring_week3 import PrometheusMetrics, LatencyTracker, RequestTracer, PerformanceOptimizer

sys.path.append("E:/Coding/PyCharm/LLM Guard/Jailbreak Detection/Jailbreak Detection System")
try:
    from hybrid_detector import HybridDetector
except ImportError:
    print("❌ ERROR: Could not load hybrid_detector.py")

# ============================================
# SETUP
# ============================================

app = FastAPI(title="LLM-Guard Proxy - Week 3 (Optimized)")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm-guard")

UPSTREAM_URL = "https://httpbin.org"

# ============================================
# INITIALIZE COMPONENTS
# ============================================

logger.info("🚀 Initializing LLM-Guard Optimized Proxy (Week 3)...")

# Detector
try:
    detector = HybridDetector(
        ml_model_path="E:/Coding\PyCharm/LLM Guard/Jailbreak Detection/Jailbreak Detection System/models/jailbreak_svm_v1.pkl",
        rules_file="E:/Coding/PyCharm/LLM Guard/Jailbreak Detection/Jailbreak Detection System/jailbreak_patterns.json"
    )
    logger.info("✅ Detector initialized")
except Exception as e:
    logger.error(f"❌ Detector init failed: {e}")
    detector = None

# Rate Limiter
rate_limiter = RateLimitingManager(
    global_rate=10.0,
    per_user_rate=5.0
)
logger.info("✅ Rate limiter initialized")

# Monitoring
prometheus_metrics = PrometheusMetrics()
latency_tracker = LatencyTracker()
request_tracer = RequestTracer()
logger.info("✅ Monitoring initialized")

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
async def health_check():
    """Health check"""
    return {
        "service": "LLM-Guard Proxy (Week 3)",
        "status": "running",
        "features": [
            "Jailbreak Detection",
            "Rate Limiting (10 req/sec)",
            "Circuit Breaker",
            "Prometheus Monitoring",
            "Distributed Tracing",
            "Latency Optimization"
        ],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        content=prometheus_metrics.export_text_format(),
        media_type="text/plain"
    )


@app.get("/metrics/summary")
async def metrics_summary():
    """Get metrics summary"""
    return prometheus_metrics.get_summary()


@app.get("/health/detailed")
async def detailed_health():
    """Detailed health status"""
    summary = prometheus_metrics.get_summary()
    suggestions = PerformanceOptimizer.suggest_optimizations(summary)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": summary,
        "optimizations": suggestions,
        "latency_tracker": latency_tracker.get_all_stats()
    }


@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get trace details"""
    return request_tracer.get_trace(trace_id)


@app.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy_optimized(
    request: Request,
    path: str,
    x_user_id: Optional[str] = Header(default="anonymous"),
    x_trace_id: Optional[str] = Header(default=None)
):
    """
    Optimized proxy with rate limiting, circuit breaker, and monitoring
    
    Headers:
        X-User-ID: User identifier
        X-Trace-ID: Distributed trace ID
    """
    
    # Generate trace ID if not provided
    if not x_trace_id:
        x_trace_id = f"{datetime.now().timestamp()}"
    
    request_tracer.start_span(x_trace_id, "request_total")
    
    request_start = time.time()
    
    logger.info(f"[{x_trace_id}] Incoming: {request.method} {path} (User: {x_user_id})")
    
    # ============================================
    # SPAN 1: RATE LIMIT CHECK
    # ============================================
    
    request_tracer.start_span(x_trace_id, "rate_limit_check")
    
    allowed, reason = await rate_limiter.check_rate_limit(x_user_id)
    
    request_tracer.end_span(x_trace_id, "rate_limit_check")
    
    if not allowed:
        logger.warning(f"[{x_trace_id}] ⚠️  Rate limited: {reason}")
        elapsed = (time.time() - request_start) * 1000
        prometheus_metrics.record_request('rate_limited', elapsed)
        latency_tracker.record_latency('rate_limit_check', elapsed)
        
        return {
            "status": "rate_limited",
            "reason": reason,
            "trace_id": x_trace_id
        }, 429
    
    # ============================================
    # SPAN 2: CIRCUIT BREAKER CHECK
    # ============================================
    
    request_tracer.start_span(x_trace_id, "circuit_breaker_check")
    
    if not rate_limiter.circuit_breaker.can_execute():
        logger.error(f"[{x_trace_id}] 🔴 Circuit breaker {rate_limiter.circuit_breaker.state}")
        elapsed = (time.time() - request_start) * 1000
        prometheus_metrics.record_request('circuit_open', elapsed)
        request_tracer.end_span(x_trace_id, "circuit_breaker_check")
        
        return {
            "status": "circuit_breaker_open",
            "state": rate_limiter.circuit_breaker.state,
            "trace_id": x_trace_id
        }, 503
    
    request_tracer.end_span(x_trace_id, "circuit_breaker_check")
    
    # ============================================
    # SPAN 3: REQUEST BODY EXTRACTION
    # ============================================
    
    request_tracer.start_span(x_trace_id, "body_extraction")
    
    body = await request.body()
    body_str = body.decode('utf-8') if body else ""
    
    request_tracer.end_span(x_trace_id, "body_extraction")
    
    # ============================================
    # SPAN 4: JAILBREAK DETECTION
    # ============================================
    
    request_tracer.start_span(x_trace_id, "jailbreak_detection")
    detection_start = time.time()
    
    if detector:
        try:
            detection_result = detector.detect(body_str)
            detection_latency = (time.time() - detection_start) * 1000
            latency_tracker.record_latency('jailbreak_detection', detection_latency)
            
            if detection_result['is_jailbreak']:
                logger.warning(
                    f"[{x_trace_id}] 🚨 JAILBREAK BLOCKED! "
                    f"Confidence: {detection_result['confidence']:.2f}"
                )
                elapsed = (time.time() - request_start) * 1000
                prometheus_metrics.record_request('jailbreak_blocked', elapsed)
                rate_limiter.circuit_breaker.record_success()
                request_tracer.end_span(x_trace_id, "jailbreak_detection")
                
                return {
                    "status": "blocked",
                    "reason": "Jailbreak detected",
                    "confidence": detection_result['confidence'],
                    "trace_id": x_trace_id
                }, 403
        
        except Exception as e:
            logger.error(f"[{x_trace_id}] Detector error: {e}")
            rate_limiter.circuit_breaker.record_failure()
    
    request_tracer.end_span(x_trace_id, "jailbreak_detection")
    
    # ============================================
    # SPAN 5: UPSTREAM REQUEST
    # ============================================
    
    request_tracer.start_span(x_trace_id, "upstream_request")
    upstream_start = time.time()
    
    logger.info(f"[{x_trace_id}] ✅ SAFE - Forwarding to upstream")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=f"{UPSTREAM_URL}/{path}",
                content=body,
                headers={
                    key: value
                    for key, value in request.headers.items()
                    if key.lower() != "host"
                }
            )
        
        upstream_latency = (time.time() - upstream_start) * 1000
        latency_tracker.record_latency('upstream_request', upstream_latency)
        
        logger.info(f"[{x_trace_id}] Response: {response.status_code}")
        
        elapsed = (time.time() - request_start) * 1000
        prometheus_metrics.record_request('success', elapsed)
        rate_limiter.circuit_breaker.record_success()
        request_tracer.end_span(x_trace_id, "upstream_request")
        request_tracer.end_span(x_trace_id, "request_total")
        
        latency_tracker.record_latency('request_total', elapsed)
        
        return {
            "status": "success",
            "passed_security_check": True,
            "upstream_status": response.status_code,
            "upstream_response": response.text,
            "latency_ms": round(elapsed, 2),
            "trace_id": x_trace_id
        }
    
    except httpx.TimeoutException:
        logger.error(f"[{x_trace_id}] ⏱️  Upstream timeout")
        elapsed = (time.time() - request_start) * 1000
        prometheus_metrics.record_request('error', elapsed)
        rate_limiter.circuit_breaker.record_failure()
        request_tracer.end_span(x_trace_id, "upstream_request")
        
        return {
            "status": "error",
            "reason": "Upstream timeout",
            "trace_id": x_trace_id
        }, 504
    
    except Exception as e:
        logger.error(f"[{x_trace_id}] 💥 Upstream error: {e}")
        elapsed = (time.time() - request_start) * 1000
        prometheus_metrics.record_request('error', elapsed)
        rate_limiter.circuit_breaker.record_failure()
        request_tracer.end_span(x_trace_id, "upstream_request")
        
        return {
            "status": "error",
            "reason": str(e),
            "trace_id": x_trace_id
        }, 502


# ============================================
# STARTUP/SHUTDOWN
# ============================================

@app.on_event("shutdown")
async def shutdown():
    logger.info("Final Metrics:")
    summary = prometheus_metrics.get_summary()
    if 'requests' in summary:
        logger.info(f"  Total Requests: {summary['requests']['total']}")
    else:
        logger.info("  No requests processed")
    
    # Cleanup traces
    request_tracer.cleanup_old_traces()


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("🚀 LLM-Guard Proxy - Week 3 (Optimized with Monitoring)")
    logger.info("=" * 70)
    logger.info("Features:")
    logger.info("  ✅ Rate Limiting (10 req/sec global, 5 req/sec per-user)")
    logger.info("  ✅ Circuit Breaker (fault tolerance)")
    logger.info("  ✅ Jailbreak Detection")
    logger.info("  ✅ Prometheus Metrics (/metrics)")
    logger.info("  ✅ Distributed Tracing (X-Trace-ID)")
    logger.info("  ✅ Latency Tracking (<100ms target)")
    logger.info("  ✅ Health Endpoints")
    logger.info("=" * 70)
    logger.info(f"📍 Listening on port 8888")
    logger.info(f"📊 Metrics at http://localhost:8888/metrics")
    logger.info("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,
        log_level="info"
    )
