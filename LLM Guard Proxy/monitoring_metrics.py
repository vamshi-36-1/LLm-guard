"""
LLM-Guard: Latency Optimization & Prometheus Monitoring
Person 1 - Week 3
Performance profiling, metrics export, and distributed tracing
"""

import time
import logging
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class LatencyTracker:
    """Track request latency across components"""
    
    def __init__(self):
        self.latencies = defaultdict(list)
        self.total_requests = 0
        self.start_time = time.time()
    
    def record_latency(self, component: str, latency_ms: float):
        """Record latency for a component"""
        self.latencies[component].append(latency_ms)
        self.total_requests += 1
    
    def get_percentiles(self, component: str) -> Dict:
        """Get latency percentiles for component"""
        if component not in self.latencies or not self.latencies[component]:
            return {}
        
        times = sorted(self.latencies[component])
        n = len(times)
        
        return {
            'min_ms': times[0],
            'p25_ms': times[n//4],
            'p50_ms': times[n//2],
            'p75_ms': times[3*n//4],
            'p95_ms': times[int(n*0.95)],
            'p99_ms': times[int(n*0.99)],
            'max_ms': times[-1],
            'mean_ms': statistics.mean(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'samples': n
        }
    
    def get_all_stats(self) -> Dict:
        """Get stats for all components"""
        stats = {}
        for component in self.latencies.keys():
            stats[component] = self.get_percentiles(component)
        
        return {
            'components': stats,
            'total_requests': self.total_requests,
            'uptime_seconds': time.time() - self.start_time
        }


class PrometheusMetrics:
    """Prometheus-compatible metrics"""
    
    def __init__(self):
        # Counters
        self.http_requests_total = 0
        self.http_requests_success = 0
        self.http_requests_rate_limited = 0
        self.http_requests_jailbreak_blocked = 0
        self.http_requests_circuit_open = 0
        self.http_requests_errors = 0
        
        # Gauges
        self.http_request_latency_ms = []
        self.active_connections = 0
        self.circuit_breaker_state = 0  # 0=CLOSED, 1=HALF_OPEN, 2=OPEN
        self.queue_depth = 0
        
        # Histograms (for distribution)
        self.latency_buckets = {
            '10': 0,
            '25': 0,
            '50': 0,
            '100': 0,
            '250': 0,
            '500': 0,
            '1000': 0,
            'inf': 0
        }
        
        self.start_time = time.time()
    
    def record_request(self, status: str, latency_ms: float):
        """Record a request"""
        self.http_requests_total += 1
        self.http_request_latency_ms.append(latency_ms)
        
        # Categorize
        if status == 'success':
            self.http_requests_success += 1
        elif status == 'rate_limited':
            self.http_requests_rate_limited += 1
        elif status == 'jailbreak_blocked':
            self.http_requests_jailbreak_blocked += 1
        elif status == 'circuit_open':
            self.http_requests_circuit_open += 1
        elif status == 'error':
            self.http_requests_errors += 1
        
        # Record in histogram buckets
        for bucket_ms in ['10', '25', '50', '100', '250', '500', '1000']:
            if latency_ms <= float(bucket_ms):
                self.latency_buckets[bucket_ms] += 1
        self.latency_buckets['inf'] += 1
    
    def export_text_format(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        timestamp = int(time.time() * 1000)
        
        # HELP and TYPE
        lines.append("# HELP http_requests_total Total HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        lines.append(f"http_requests_total{{status=\"total\"}} {self.http_requests_total} {timestamp}")
        lines.append(f"http_requests_total{{status=\"success\"}} {self.http_requests_success} {timestamp}")
        lines.append(f"http_requests_total{{status=\"rate_limited\"}} {self.http_requests_rate_limited} {timestamp}")
        lines.append(f"http_requests_total{{status=\"jailbreak_blocked\"}} {self.http_requests_jailbreak_blocked} {timestamp}")
        lines.append(f"http_requests_total{{status=\"circuit_open\"}} {self.http_requests_circuit_open} {timestamp}")
        lines.append(f"http_requests_total{{status=\"errors\"}} {self.http_requests_errors} {timestamp}")
        
        # Latency histogram
        lines.append("")
        lines.append("# HELP http_request_duration_ms Request duration in milliseconds")
        lines.append("# TYPE http_request_duration_ms histogram")
        
        for bucket, count in self.latency_buckets.items():
            lines.append(f'http_request_duration_ms_bucket{{le="{bucket}"}} {count} {timestamp}')
        
        if self.http_requests_total > 0:
            avg_latency = statistics.mean(self.http_request_latency_ms)
        else:
            avg_latency = 0
        
        lines.append(f"http_request_duration_ms_sum {sum(self.http_request_latency_ms) if self.http_request_latency_ms else 0} {timestamp}")
        lines.append(f"http_request_duration_ms_count {self.http_requests_total} {timestamp}")
        
        # Circuit breaker
        lines.append("")
        lines.append("# HELP circuit_breaker_state Circuit breaker state")
        lines.append("# TYPE circuit_breaker_state gauge")
        lines.append(f"circuit_breaker_state {self.circuit_breaker_state} {timestamp}")
        
        # Queue depth
        lines.append("")
        lines.append("# HELP queue_depth Current queue depth")
        lines.append("# TYPE queue_depth gauge")
        lines.append(f"queue_depth {self.queue_depth} {timestamp}")
        
        # Uptime
        lines.append("")
        lines.append("# HELP process_uptime_seconds Process uptime")
        lines.append("# TYPE process_uptime_seconds gauge")
        lines.append(f"process_uptime_seconds {time.time() - self.start_time} {timestamp}")
        
        return "\n".join(lines)
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        if self.http_requests_total == 0:
            return {'status': 'no_data'}
        
        latencies = sorted(self.http_request_latency_ms)
        n = len(latencies)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'requests': {
                'total': self.http_requests_total,
                'success': self.http_requests_success,
                'success_rate': self.http_requests_success / self.http_requests_total,
                'rate_limited': self.http_requests_rate_limited,
                'jailbreak_blocked': self.http_requests_jailbreak_blocked,
                'circuit_open': self.http_requests_circuit_open,
                'errors': self.http_requests_errors
            },
            'latency_ms': {
                'min': latencies[0],
                'p50': latencies[n//2],
                'p95': latencies[int(n*0.95)],
                'p99': latencies[int(n*0.99)],
                'max': latencies[-1],
                'mean': statistics.mean(latencies),
                'stdev': statistics.stdev(latencies)
            },
            'sla_compliance': {
                'target_ms': 100,
                'p99_ms': latencies[int(n*0.99)],
                'meets_sla': latencies[int(n*0.99)] < 100
            }
        }


class RequestTracer:
    """Distributed tracing for requests"""
    
    def __init__(self):
        self.traces = defaultdict(dict)
    
    def start_span(self, trace_id: str, span_name: str):
        """Start a span"""
        if trace_id not in self.traces:
            self.traces[trace_id] = {
                'spans': [],
                'start_time': time.time()
            }
        
        self.traces[trace_id]['spans'].append({
            'name': span_name,
            'start': time.time(),
            'end': None,
            'duration_ms': None
        })
    
    def end_span(self, trace_id: str, span_name: str):
        """End a span"""
        if trace_id in self.traces:
            for span in self.traces[trace_id]['spans']:
                if span['name'] == span_name and span['end'] is None:
                    span['end'] = time.time()
                    span['duration_ms'] = (span['end'] - span['start']) * 1000
                    break
    
    def get_trace(self, trace_id: str) -> Dict:
        """Get trace details"""
        if trace_id not in self.traces:
            return {}
        
        trace = self.traces[trace_id]
        total_duration = time.time() - trace['start_time']
        
        return {
            'trace_id': trace_id,
            'total_duration_ms': total_duration * 1000,
            'spans': trace['spans']
        }
    
    def cleanup_old_traces(self, max_age_seconds: int = 3600):
        """Remove old traces"""
        current_time = time.time()
        to_delete = []
        
        for trace_id, trace in self.traces.items():
            if current_time - trace['start_time'] > max_age_seconds:
                to_delete.append(trace_id)
        
        for trace_id in to_delete:
            del self.traces[trace_id]
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old traces")


class PerformanceOptimizer:
    """Optimize proxy performance"""
    
    @staticmethod
    def suggest_optimizations(metrics_summary: Dict) -> List[str]:
        """Suggest optimizations based on metrics"""
        suggestions = []
        
        if 'latency_ms' not in metrics_summary:
            return suggestions
        
        latency = metrics_summary['latency_ms']
        
        # Check latency
        if latency['p99'] > 100:
            suggestions.append(
                f"⚠️  P99 latency is {latency['p99']:.1f}ms (target: <100ms). "
                "Consider: increasing connection pooling, enabling caching, or optimizing upstream"
            )
        
        # Check error rate
        if 'requests' in metrics_summary:
            error_rate = metrics_summary['requests']['errors'] / metrics_summary['requests']['total']
            if error_rate > 0.05:
                suggestions.append(
                    f"⚠️  Error rate is {error_rate*100:.1f}% (target: <1%). "
                    "Check upstream service health and circuit breaker state"
                )
        
        # Check success rate
        if 'requests' in metrics_summary:
            success_rate = metrics_summary['requests']['success_rate']
            if success_rate < 0.95:
                suggestions.append(
                    f"⚠️  Success rate is {success_rate*100:.1f}% (target: >95%). "
                    "Review rate limiting and circuit breaker thresholds"
                )
        
        if not suggestions:
            suggestions.append("✅ Proxy performance is healthy!")
        
        return suggestions


if __name__ == "__main__":
    # Test metrics
    metrics = PrometheusMetrics()
    
    # Simulate requests
    for i in range(100):
        latency = 20 + (i % 50)  # Vary latency
        status = 'success' if i % 10 != 0 else 'rate_limited'
        metrics.record_request(status, latency)
    
    print("📊 Metrics Summary:")
    print(metrics.get_summary())
    
    print("\n📈 Prometheus Format:")
    print(metrics.export_text_format()[:500] + "...")  # First 500 chars
