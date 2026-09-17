"""
LLM-Guard: Production Monitoring
Person 2 - Week 4
Prometheus metrics and monitoring setup
"""

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class ProductionMetrics:
    """Production monitoring metrics"""
    
    def __init__(self):
        # Detection metrics
        self.detections_total = 0
        self.detections_jailbreak = 0
        self.detections_benign = 0
        
        # Performance metrics
        self.inference_times = []
        self.errors_total = 0
        
        # Accuracy metrics
        self.accuracy_score = 0.0
        self.accuracy_updated_at = None
        
        # SLA metrics
        self.uptime_seconds = 0
        self.downtime_seconds = 0
    
    def record_detection(self, is_jailbreak: bool, latency_ms: float):
        """Record detection metrics"""
        self.detections_total += 1
        
        if is_jailbreak:
            self.detections_jailbreak += 1
        else:
            self.detections_benign += 1
        
        self.inference_times.append(latency_ms)
    
    def record_error(self):
        """Record error"""
        self.errors_total += 1
    
    def record_accuracy(self, accuracy: float):
        """Record accuracy score"""
        self.accuracy_score = accuracy
        self.accuracy_updated_at = datetime.now().isoformat()
    
    def get_metrics_summary(self) -> Dict:
        """Get all metrics summary"""
        if len(self.inference_times) > 0:
            latencies = sorted(self.inference_times)
            n = len(latencies)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'detections': {
                    'total': self.detections_total,
                    'jailbreak': self.detections_jailbreak,
                    'benign': self.detections_benign,
                    'jailbreak_rate': (
                        self.detections_jailbreak / self.detections_total 
                        if self.detections_total > 0 else 0
                    )
                },
                'latency_ms': {
                    'min': latencies[0],
                    'p50': latencies[n//2],
                    'p95': latencies[int(n*0.95)],
                    'p99': latencies[int(n*0.99)],
                    'max': latencies[-1],
                    'avg': sum(latencies) / len(latencies)
                },
                'errors': {
                    'total': self.errors_total,
                    'error_rate': (
                        self.errors_total / self.detections_total
                        if self.detections_total > 0 else 0
                    )
                },
                'accuracy': {
                    'score': self.accuracy_score,
                    'updated_at': self.accuracy_updated_at
                }
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'no_data_yet'
        }


class PrometheusExporter:
    """Export metrics in Prometheus format"""
    
    def __init__(self, metrics: ProductionMetrics):
        self.metrics = metrics
    
    def export_text_format(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        
        summary = self.metrics.get_metrics_summary()
        
        # Detections
        lines.append(f"# HELP llm_guard_detections_total Total detections")
        lines.append(f"# TYPE llm_guard_detections_total counter")
        lines.append(f'llm_guard_detections_total{{type="total"}} {summary["detections"]["total"]}')
        lines.append(f'llm_guard_detections_total{{type="jailbreak"}} {summary["detections"]["jailbreak"]}')
        lines.append(f'llm_guard_detections_total{{type="benign"}} {summary["detections"]["benign"]}')
        
        # Latency
        lines.append(f"# HELP llm_guard_latency_ms Inference latency")
        lines.append(f"# TYPE llm_guard_latency_ms gauge")
        for percentile, value in summary['latency_ms'].items():
            lines.append(f'llm_guard_latency_ms{{percentile="{percentile}"}} {value:.2f}')
        
        # Errors
        lines.append(f"# HELP llm_guard_errors_total Total errors")
        lines.append(f"# TYPE llm_guard_errors_total counter")
        lines.append(f'llm_guard_errors_total {{}} {summary["errors"]["total"]}')
        lines.append(f'llm_guard_error_rate {{}} {summary["errors"]["error_rate"]:.4f}')
        
        # Accuracy
        lines.append(f"# HELP llm_guard_accuracy Detector accuracy")
        lines.append(f"# TYPE llm_guard_accuracy gauge")
        lines.append(f'llm_guard_accuracy {{}} {summary["accuracy"]["score"]:.4f}')
        
        return "\n".join(lines)


class AlertManager:
    """Manage production alerts"""
    
    # SLA Thresholds
    LATENCY_WARNING_MS = 100
    LATENCY_CRITICAL_MS = 150
    ERROR_RATE_WARNING = 0.01
    ERROR_RATE_CRITICAL = 0.05
    ACCURACY_WARNING = 0.85
    ACCURACY_CRITICAL = 0.80
    
    @staticmethod
    def check_alerts(metrics_summary: Dict) -> List[Dict]:
        """Check for alert conditions"""
        alerts = []
        
        # Latency alerts
        p99_latency = metrics_summary['latency_ms']['p99']
        
        if p99_latency > AlertManager.LATENCY_CRITICAL_MS:
            alerts.append({
                'severity': 'critical',
                'title': 'High Latency (P99)',
                'message': f'P99 latency is {p99_latency:.2f}ms (>150ms)',
                'metric': 'latency_p99',
                'value': p99_latency
            })
        elif p99_latency > AlertManager.LATENCY_WARNING_MS:
            alerts.append({
                'severity': 'warning',
                'title': 'Elevated Latency (P99)',
                'message': f'P99 latency is {p99_latency:.2f}ms (>100ms)',
                'metric': 'latency_p99',
                'value': p99_latency
            })
        
        # Error rate alerts
        error_rate = metrics_summary['errors']['error_rate']
        
        if error_rate > AlertManager.ERROR_RATE_CRITICAL:
            alerts.append({
                'severity': 'critical',
                'title': 'High Error Rate',
                'message': f'Error rate is {error_rate*100:.2f}% (>5%)',
                'metric': 'error_rate',
                'value': error_rate
            })
        elif error_rate > AlertManager.ERROR_RATE_WARNING:
            alerts.append({
                'severity': 'warning',
                'title': 'Elevated Error Rate',
                'message': f'Error rate is {error_rate*100:.2f}% (>1%)',
                'metric': 'error_rate',
                'value': error_rate
            })
        
        # Accuracy alerts
        accuracy = metrics_summary['accuracy']['score']
        
        if accuracy < AlertManager.ACCURACY_CRITICAL:
            alerts.append({
                'severity': 'critical',
                'title': 'Low Accuracy',
                'message': f'Detector accuracy is {accuracy*100:.2f}% (<80%)',
                'metric': 'accuracy',
                'value': accuracy
            })
        elif accuracy < AlertManager.ACCURACY_WARNING:
            alerts.append({
                'severity': 'warning',
                'title': 'Accuracy Degradation',
                'message': f'Detector accuracy is {accuracy*100:.2f}% (<85%)',
                'metric': 'accuracy',
                'value': accuracy
            })
        
        return alerts


class HealthCheck:
    """Production health check"""
    
    def __init__(self, metrics: ProductionMetrics):
        self.metrics = metrics
    
    def get_health_status(self) -> Dict:
        """Get overall health status"""
        summary = self.metrics.get_metrics_summary()
        
        # Check each component
        latency_ok = summary['latency_ms']['p99'] < 100
        error_rate_ok = summary['errors']['error_rate'] < 0.01
        accuracy_ok = summary['accuracy']['score'] > 0.85
        
        overall_healthy = latency_ok and error_rate_ok and accuracy_ok
        
        return {
            'status': 'healthy' if overall_healthy else 'degraded',
            'latency': 'ok' if latency_ok else 'warning',
            'errors': 'ok' if error_rate_ok else 'warning',
            'accuracy': 'ok' if accuracy_ok else 'warning',
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    metrics = ProductionMetrics()
    
    # Simulate some detections
    metrics.record_detection(False, 45.3)
    metrics.record_detection(True, 52.1)
    metrics.record_detection(False, 48.9)
    metrics.record_accuracy(0.87)
    
    # Export metrics
    exporter = PrometheusExporter(metrics)
    prometheus_text = exporter.export_text_format()
    print(prometheus_text)
    
    # Check health
    health_check = HealthCheck(metrics)
    print("\nHealth Status:")
    print(health_check.get_health_status())
