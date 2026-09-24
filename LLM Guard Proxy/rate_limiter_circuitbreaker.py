"""
LLM-Guard: Rate Limiting & Request Queueing
Week 2
Implements token bucket rate limiting and request queue
"""

import asyncio
import time
from typing import Optional, Dict
from collections import defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TokenBucketRateLimiter:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, rate: float = 10.0, capacity: int = 20):
        """
        Initialize rate limiter
        
        Args:
            rate: Tokens per second (requests/sec)
            capacity: Max tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.request_count = 0
        self.rejected_count = 0
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens based on rate
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now
    
    def allow_request(self) -> bool:
        """
        Check if request is allowed
        
        Returns:
            True if request allowed, False if rate limit exceeded
        """
        self._refill()
        
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            self.request_count += 1
            return True
        else:
            self.rejected_count += 1
            return False
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return {
            'current_tokens': round(self.tokens, 2),
            'capacity': self.capacity,
            'rate': self.rate,
            'allowed_requests': self.request_count,
            'rejected_requests': self.rejected_count,
            'rejection_rate': (
                self.rejected_count / (self.request_count + self.rejected_count)
                if (self.request_count + self.rejected_count) > 0 else 0
            )
        }


class RequestQueue:
    """Queue for handling burst traffic"""
    
    def __init__(self, max_queue_size: int = 100, timeout_sec: float = 30.0):
        """
        Initialize request queue
        
        Args:
            max_queue_size: Max requests in queue
            timeout_sec: Request timeout in queue
        """
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.timeout_sec = timeout_sec
        self.enqueued = 0
        self.processed = 0
        self.timed_out = 0
    
    async def enqueue(self, request_id: str) -> bool:
        """
        Enqueue request
        
        Returns:
            True if enqueued, False if queue full
        """
        try:
            self.queue.put_nowait((request_id, time.time()))
            self.enqueued += 1
            return True
        except asyncio.QueueFull:
            logger.warning(f"Request queue full, rejecting {request_id}")
            return False
    
    async def dequeue(self) -> Optional[str]:
        """
        Dequeue and process request
        
        Returns:
            Request ID if available, None if timed out
        """
        try:
            request_id, enqueue_time = await asyncio.wait_for(
                self.queue.get(),
                timeout=self.timeout_sec
            )
            
            wait_time = time.time() - enqueue_time
            
            if wait_time > self.timeout_sec:
                self.timed_out += 1
                logger.warning(f"Request {request_id} timed out in queue ({wait_time:.2f}s)")
                return None
            
            self.processed += 1
            return request_id
        except asyncio.TimeoutError:
            self.timed_out += 1
            return None
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        return {
            'queue_size': self.queue.qsize(),
            'max_size': self.queue.maxsize,
            'enqueued': self.enqueued,
            'processed': self.processed,
            'timed_out': self.timed_out
        }


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_check_time = time.time()
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            logger.info("🔄 Circuit Breaker: HALF_OPEN → CLOSED")
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.error(f"⚠️  Circuit Breaker: CLOSED → OPEN (failures: {self.failure_count})")
    
    def can_execute(self) -> bool:
        """
        Check if request can execute
        
        Returns:
            True if circuit allows, False if open
        """
        if self.state == 'CLOSED':
            return True
        
        if self.state == 'OPEN':
            # Check if enough time passed to try recovery
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                self.success_count = 0
                logger.info("🔄 Circuit Breaker: OPEN → HALF_OPEN (attempting recovery)")
                return True
            else:
                return False
        
        if self.state == 'HALF_OPEN':
            # Allow limited requests in half-open state
            return self.success_count < 3
        
        return False
    
    def get_status(self) -> Dict:
        """Get circuit breaker status"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'threshold': self.failure_threshold,
            'last_failure': self.last_failure_time
        }


class RateLimitingManager:
    """Centralized rate limiting for all users/clients"""
    
    def __init__(self, global_rate: float = 100.0, per_user_rate: float = 10.0):
        """
        Initialize rate limiting manager
        
        Args:
            global_rate: Global requests per second
            per_user_rate: Per-user requests per second
        """
        self.global_limiter = TokenBucketRateLimiter(rate=global_rate, capacity=int(global_rate*2))
        self.user_limiters: Dict[str, TokenBucketRateLimiter] = defaultdict(
            lambda: TokenBucketRateLimiter(rate=per_user_rate, capacity=int(per_user_rate*2))
        )
        self.queue = RequestQueue()
        self.circuit_breaker = CircuitBreaker()
    
    async def check_rate_limit(self, user_id: str = "anonymous") -> tuple[bool, str]:
        """
        Check if request is allowed
        
        Returns:
            (allowed, reason)
        """
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            return False, f"Circuit breaker is {self.circuit_breaker.state}"
        
        # Check global rate limit
        if not self.global_limiter.allow_request():
            logger.warning(f"Global rate limit exceeded")
            return False, "Global rate limit exceeded"
        
        # Check per-user rate limit
        if not self.user_limiters[user_id].allow_request():
            logger.warning(f"User rate limit exceeded for {user_id}")
            return False, f"User rate limit exceeded"
        
        return True, "Allowed"
    
    async def handle_burst(self, request_id: str) -> bool:
        """
        Handle burst traffic via queue
        
        Returns:
            True if queued, False if queue full
        """
        return await self.queue.enqueue(request_id)
    
    def get_stats(self) -> Dict:
        """Get all rate limiting statistics"""
        return {
            'global_limiter': self.global_limiter.get_stats(),
            'circuit_breaker': self.circuit_breaker.get_status(),
            'queue': self.queue.get_stats(),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test rate limiter
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=20)
    
    print("Testing Rate Limiter...")
    for i in range(15):
        allowed = limiter.allow_request()
        print(f"Request {i+1}: {'✅ ALLOWED' if allowed else '❌ REJECTED'}")
    
    print("\nRate Limiter Stats:")
    print(limiter.get_stats())
    
    print("\nTesting Circuit Breaker...")
    cb = CircuitBreaker(failure_threshold=3)
    
    for i in range(5):
        if cb.can_execute():
            print(f"Request {i+1}: Can execute ({cb.state})")
            if i < 2:
                cb.record_failure()
                print(f"  → Recorded failure (count: {cb.failure_count})")
            else:
                cb.record_success()
                print(f"  → Recorded success")
        else:
            print(f"Request {i+1}: Cannot execute ({cb.state})")
    
    print("\nCircuit Breaker Status:")
    print(cb.get_status())
