"""
LLM-Guard: Complete Reverse Proxy with Jailbreak Detection
(Backend/Proxy) + (Detector)

This proxy:
1. Receives user requests
2. Checks with YOUR jailbreak detector
3. If JAILBREAK → Block request
4. If SAFE → Forward to LLM API
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import logging
import sys
import os
from datetime import datetime

sys.path.append("../Jailbreak Detection System")
try:
    from hybrid_detector import HybridDetector
except ImportError:
    print("❌ ERROR: Could not load hybrid_detector.py")
    print("Make sure the path is correct!")

# ============================================
# SETUP
# ============================================

app = FastAPI(title="LLM-Guard Proxy")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm-guard")

# Configure upstream URL (the actual LLM API)
UPSTREAM_URL = "https://httpbin.org"  # Replace with real LLM API

# ============================================
# INITIALIZE YOUR DETECTOR (PERSON 2'S WORK)
# ============================================

logger.info("🚀 Initializing LLM-Guard Jailbreak Detector...")

try:
    detector = HybridDetector(
        ml_model_path="../Jailbreak Detection System/models/jailbreak_svm_v1.pkl",
        rules_file="../Jailbreak Detection System/jailbreak_patterns.json"
    )
    logger.info("✅ Detector initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize detector: {e}")
    detector = None

# ============================================
# METRICS TRACKING
# ============================================

class ProxyMetrics:
    """Track proxy performance"""
    def __init__(self):
        self.total_requests = 0
        self.blocked_requests = 0
        self.allowed_requests = 0
        self.errors = 0
    
    def get_stats(self):
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "blocked_rate": (self.blocked_requests / max(self.total_requests, 1)) * 100,
            "allowed_requests": self.allowed_requests,
            "errors": self.errors
        }

metrics = ProxyMetrics()

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "LLM-Guard Proxy",
        "status": "running",
        "detector": "active" if detector else "inactive",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Get proxy metrics"""
    return metrics.get_stats()


@app.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy(request: Request, path: str):
    """
    Main proxy endpoint with jailbreak detection
    
    Flow:
    1. Extract request body
    2. Check with detector (YOUR CODE!)
    3. If jailbreak → BLOCK
    4. If safe → FORWARD
    """
    
    metrics.total_requests += 1
    
    # ============================================
    # STEP 1: EXTRACT REQUEST
    # ============================================
    
    target_url = f"{UPSTREAM_URL}/{path}"
    body = await request.body()
    body_str = body.decode('utf-8') if body else ""
    
    request_id = f"{datetime.now().timestamp()}"
    
    logger.info(f"[{request_id}] Incoming: {request.method} {path}")
    
    # ============================================
    # STEP 2: CHECK WITH YOUR DETECTOR
    # ============================================
    
    if not detector:
        logger.error("❌ Detector not initialized!")
        metrics.errors += 1
        return {
            "status": "error",
            "reason": "Detector not available",
            "allowed_to_pass": True  # Fail open (allow if detector fails)
        }
    
    try:
        detection_result = detector.detect(body_str)
    except Exception as e:
        logger.error(f"[{request_id}] Detector error: {e}")
        metrics.errors += 1
        return {
            "status": "error",
            "reason": f"Detection failed: {str(e)}",
            "allowed_to_pass": True  # Fail open
        }
    
    # ============================================
    # STEP 3: CHECK VERDICT
    # ============================================
    
    if detection_result['is_jailbreak']:
        # BLOCK THIS REQUEST
        metrics.blocked_requests += 1
        
        logger.warning(
            f"[{request_id}] 🚨 JAILBREAK BLOCKED!"
            f" Method: {detection_result['method']}"
            f" | Confidence: {detection_result['confidence']:.2f}"
            f" | Reason: {detection_result['reason']}"
        )
        
        return JSONResponse(
            status_code=403,
            content={
                "status": "blocked",
                "reason": "Jailbreak attempt detected",
                "details": {
                    "method": detection_result['method'],
                    "confidence": detection_result['confidence'],
                    "reason": detection_result['reason']
                },
                "request_id": request_id
            }
        )
    
    # SAFE - Continue to LLM
    metrics.allowed_requests += 1
    
    logger.info(
        f"[{request_id}] ✅ SAFE - Forwarding to LLM"
        f" | Confidence: {detection_result['confidence']:.2f}"
    )
    
    # ============================================
    # STEP 4: FORWARD TO UPSTREAM (IF SAFE)
    # ============================================
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers={
                    key: value
                    for key, value in request.headers.items()
                    if key.lower() != "host"
                }
            )
        
        logger.info(
            f"[{request_id}] Response from upstream: {response.status_code}"
        )
        
        return {
            "status": "success",
            "passed_security_check": True,
            "upstream_status": response.status_code,
            "upstream_response": response.text,
            "request_id": request_id
        }
    
    except httpx.TimeoutException:
        logger.error(f"[{request_id}] ⏱️  Upstream timeout")
        metrics.errors += 1
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
        metrics.errors += 1
        return JSONResponse(
            status_code=502,
            content={
                "status": "error",
                "reason": f"Upstream error: {str(e)}",
                "request_id": request_id
            }
        )


# ============================================
# RUN THE PROXY
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("🚀 LLM-Guard Proxy Starting")
    logger.info("=" * 60)
    logger.info("📍 Upstream URL: " + UPSTREAM_URL)
    logger.info("🛡️  Jailbreak Detector: " + ("Active ✅" if detector else "Inactive ❌"))
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
