"""
LLM-Guard: Advanced Proxy with Rate Limiting & Circuit Breaker
Person 1 - Week 2
Integrates rate limiting, request queueing, and circuit breaker
"""

from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import httpx
import logging
from datetime import datetime
import sys
from typing import Optional

# Import rate limiting components
from rate_limiter import RateLimitingManager, CircuitBreaker

sys.path.append("E:/Coding/PyCharm/LLM Guard/Jailbreak Detection/Jailbreak Detection System")
try:
    from hybrid_detector import HybridDetector
except ImportError:
    print("❌ ERROR: Could not load hybrid_detector.py")

# ============================================
# SETUP
# ============================================

app = FastAPI(title="LLM-Guard Proxy - Week 2")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm-guard")

UPSTREAM_URL = "https://httpbin.org"

# ============================================
# INITIALIZE COMPONENTS
# ============================================

logger.info("🚀 Initializing LLM-Guard Advanced Proxy...")

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

# Rate Limiting Manager
rate_limiter = RateLimitingManager(
    global_rate=10.0,      # 10 requests/sec globally
    per_user_rate=5.0      # 5 requests/sec per user
)

# ============================================
# METRICS
# ============================================

class ProxyMetrics:
    """Track proxy performance"""
    def __init__(self):
        self.total_requests = 0
        self.allowed_requests = 0
        self.rate_limited = 0
        self.blocked_jailbreak = 0
        self.circuit_open = 0
        self.queue_full = 0
        self.upstream_errors = 0
    
    def get_stats(self):
        return {
            "total_requests": self.total_requests,
            "allowed_through": self.allowed_requests,
            "rate_limited": self.rate_limited,
            "blocked_jailbreak": self.blocked_jailbreak,
            "circuit_breaker_rejections": self.circuit_open,
            "queue_full_rejections": self.queue_full,
            "upstream_errors": self.upstream_errors,
            "timestamp": datetime.now().isoformat()
        }

metrics = ProxyMetrics()

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
async def health_check():
    """Health check"""
    return {
        "service": "LLM-Guard Proxy (Week 2)",
        "status": "running",
        "detector": "active" if detector else "inactive",
        "rate_limiter": "active",
        "circuit_breaker": "active",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Get proxy metrics"""
    return {
        "proxy": metrics.get_stats(),
        "rate_limiter": rate_limiter.get_stats()
    }


@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check"""
    return {
        "service": "LLM-Guard Proxy",
        "status": "healthy",
        "detector": {
            "status": "active" if detector else "inactive"
        },
        "rate_limiter": {
            "status": "active",
            "stats": rate_limiter.global_limiter.get_stats()
        },
        "circuit_breaker": {
            "status": rate_limiter.circuit_breaker.state,
            "details": rate_limiter.circuit_breaker.get_status()
        },
        "queue": {
            "stats": rate_limiter.queue.get_stats()
        }
    }


@app.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy_with_rate_limiting(
    request: Request,
    path: str,
    x_user_id: Optional[str] = Header(default="anonymous")
):
    """
    Advanced proxy with rate limiting and circuit breaker
    
    Headers:
        X-User-ID: User identifier for per-user rate limiting
    """
    
    metrics.total_requests += 1
    request_id = f"{datetime.now().timestamp()}"
    
    logger.info(f"[{request_id}] Incoming: {request.method} {path} (User: {x_user_id})")
    
    # ============================================
    # STEP 1: CHECK RATE LIMIT
    # ============================================
    
    allowed, reason = await rate_limiter.check_rate_limit(x_user_id)
    
    if not allowed:
        logger.warning(f"[{request_id}] ⚠️  Rate limited: {reason}")
        metrics.rate_limited += 1
        
        return JSONResponse(
            status_code=429,
            content={
                "status": "rate_limited",
                "reason": reason,
                "request_id": request_id
            }
        )
    
    # ============================================
    # STEP 2: CHECK CIRCUIT BREAKER
    # ============================================
    
    if not rate_limiter.circuit_breaker.can_execute():
        logger.error(f"[{request_id}] 🔴 Circuit breaker OPEN")
        metrics.circuit_open += 1
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "service_unavailable",
                "reason": f"Circuit breaker is {rate_limiter.circuit_breaker.state}",
                "request_id": request_id
            }
        )
    
    # ============================================
    # STEP 3: EXTRACT REQUEST
    # ============================================
    
    body = await request.body()
    body_str = body.decode('utf-8') if body else ""
    
    # ============================================
    # STEP 4: JAILBREAK DETECTION
    # ============================================
    
    if detector:
        try:
            detection_result = detector.detect(body_str)
            
            if detection_result['is_jailbreak']:
                logger.warning(
                    f"[{request_id}] 🚨 JAILBREAK BLOCKED! "
                    f"Method: {detection_result['method']} | "
                    f"Confidence: {detection_result['confidence']:.2f}"
                )
                metrics.blocked_jailbreak += 1
                
                rate_limiter.circuit_breaker.record_success()
                
                return JSONResponse(
                    status_code=403,
                    content={
                        "status": "blocked",
                        "reason": "Jailbreak detected",
                        "details": {
                            "method": detection_result['method'],
                            "confidence": detection_result['confidence'],
                            "reason": detection_result['reason']
                        },
                        "request_id": request_id
                    }
                )
        
        except Exception as e:
            logger.error(f"[{request_id}] Detector error: {e}")
            rate_limiter.circuit_breaker.record_failure()
    
    # ============================================
    # STEP 5: FORWARD TO UPSTREAM
    # ============================================
    
    logger.info(f"[{request_id}] ✅ SAFE - Forwarding to upstream")
    
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
        
        logger.info(f"[{request_id}] Response: {response.status_code}")
        metrics.allowed_requests += 1
        
        # Record success in circuit breaker
        rate_limiter.circuit_breaker.record_success()
        
        return {
            "status": "success",
            "passed_security_check": True,
            "upstream_status": response.status_code,
            "upstream_response": response.text,
            "request_id": request_id
        }
    
    except httpx.TimeoutException:
        logger.error(f"[{request_id}] ⏱️  Upstream timeout")
        metrics.upstream_errors += 1
        rate_limiter.circuit_breaker.record_failure()
        
        return JSONResponse(
            status_code=504,
            content={
                "status": "error",
                "reason": "Upstream timeout",
                "request_id": request_id
            }
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] 💥 Upstream error: {e}")
        metrics.upstream_errors += 1
        rate_limiter.circuit_breaker.record_failure()
        
        return JSONResponse(
            status_code=502,
            content={
                "status": "error",
                "reason": f"Upstream error: {str(e)}",
                "request_id": request_id
            }
        )


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("🚀 LLM-Guard Proxy - Week 2 (Rate Limiting & Circuit Breaker)")
    logger.info("=" * 70)
    logger.info("📍 Upstream URL: " + UPSTREAM_URL)
    logger.info("🛡️  Jailbreak Detector: " + ("Active ✅" if detector else "Inactive ❌"))
    logger.info("⏱️  Rate Limiter: Active (10 req/sec global, 5 req/sec per-user)")
    logger.info("🔄 Circuit Breaker: Active")
    logger.info("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,  # Person 1 uses port 8888
        log_level="info"
    )
