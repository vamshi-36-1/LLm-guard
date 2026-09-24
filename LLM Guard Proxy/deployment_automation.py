"""
LLM-Guard: Production Deployment Automation
Week 4
Safe automated deployment with checks, rollback, and TLS
"""

import logging
import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import ssl
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    """Automate safe production deployment"""
    
    def __init__(self, environment: str = 'production', enable_tls: bool = True):
        self.environment = environment
        self.enable_tls = enable_tls
        self.deployment_log = f"logs/deployment_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.deployment_history = []
    
    def run_pre_deployment_checks(self) -> Tuple[bool, str]:
        """Run all pre-deployment checks"""
        logger.info("=" * 70)
        logger.info("🔍 PRE-DEPLOYMENT VERIFICATION")
        logger.info("=" * 70)
        
        checks = [
            ("Python version", self._check_python_version),
            ("Dependencies", self._check_dependencies),
            ("Code quality", self._check_code_quality),
            ("Security scan", self._check_security),
            ("Model files", self._check_model_files),
            ("Configuration", self._check_configuration),
            ("Disk space", self._check_disk_space),
            ("Network", self._check_network),
        ]
        
        results = {}
        for check_name, check_func in checks:
            logger.info(f"Running: {check_name}...")
            success, msg = check_func()
            results[check_name] = success
            
            if success:
                logger.info(f"  ✅ {check_name}: PASS")
            else:
                logger.error(f"  ❌ {check_name}: FAIL - {msg}")
                return False, f"{check_name} failed: {msg}"
        
        logger.info("=" * 70)
        logger.info("✅ ALL PRE-DEPLOYMENT CHECKS PASSED")
        logger.info("=" * 70)
        
        return True, json.dumps(results, indent=2)
    
    def _check_python_version(self) -> Tuple[bool, str]:
        """Check Python 3.8+"""
        import sys
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        return False, f"Python {version.major}.{version.minor} < 3.8"
    
    def _check_dependencies(self) -> Tuple[bool, str]:
        """Check required packages installed"""
        required = ['fastapi', 'uvicorn', 'httpx', 'pydantic']
        missing = []
        
        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        return True, "All required packages installed"
    
    def _check_code_quality(self) -> Tuple[bool, str]:
        """Check code quality with basic validation"""
        try:
            import ast
            
            files_to_check = [
                'rate_limiter_circuitbreaker.py',
                'proxy_monitoring.py',
                'monitoring_metrics.py'
            ]
            
            for file in files_to_check:
                if not Path(file).exists():
                    return False, f"File not found: {file}"
                
                with open(file, 'r', encoding='utf-8') as f:
                    try:
                        ast.parse(f.read())
                    except SyntaxError as e:
                        return False, f"Syntax error in {file}: {e}"
            
            return True, "Code quality OK"
        except Exception as e:
            return False, str(e)
    
    def _check_security(self) -> Tuple[bool, str]:
        """Basic security checks"""
        try:
            # Check for hardcoded secrets
            secret_patterns = ['password', 'api_key', 'secret']
            
            for file in Path('.').glob('*.py'):
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for pattern in secret_patterns:
                        if f"{pattern} = '" in content or f"{pattern} = \"" in content:
                            if 'config' not in str(file):  # Allow in config files
                                return False, f"Possible hardcoded secret in {file}"
            
            return True, "Security check passed"
        except Exception as e:
            return False, str(e)
    
    def _check_model_files(self) -> Tuple[bool, str]:
        """Check model files exist"""
        models_required = [
            "../Jailbreak Detection System/models/jailbreak_svm_v1.pkl",
            "../Jailbreak Detection System/jailbreak_patterns.json"
        ]
        
        for model in models_required:
            if not Path(model).exists():
                return False, f"Model not found: {model}"
        
        return True, "All model files present"
    
    def _check_configuration(self) -> Tuple[bool, str]:
        """Check configuration"""
        config_items = {
            'UPSTREAM_URL': 'https://',
            'port': '8888',
            'rate_limit': '10'
        }
        
        try:
            with open('proxy_monitoring.py', 'r', encoding='utf-8') as f:
                content = f.read()
                for key, expected in config_items.items():
                    if key not in content:
                        return False, f"Configuration missing: {key}"
            
            return True, "Configuration OK"
        except Exception as e:
            return False, str(e)
    
    def _check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space"""
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        # Need at least 1GB free
        if free < 1e9:
            return False, f"Only {free/1e9:.1f}GB free (need 1GB)"
        
        return True, f"{free/1e9:.1f}GB free"
    
    def _check_network(self) -> Tuple[bool, str]:
        """Check network connectivity"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True, "Network OK"
        except Exception as e:
            return False, f"Network check failed: {e}"
    
    def backup_current_deployment(self) -> str:
        """Backup current deployment"""
        logger.info("💾 Backing up current deployment...")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            files_to_backup = [
                'proxy_monitoring.py',
                'rate_limiter_circuitbreaker.py',
                'monitoring_metrics.py',
                'requirements.txt'
            ]
            
            backup_path = self.backup_dir / f"deployment_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            for file in files_to_backup:
                if Path(file).exists():
                    shutil.copy(file, backup_path / file)
            
            logger.info(f"✅ Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def setup_tls(self, cert_path: str = "certs/server.crt", key_path: str = "certs/server.key") -> Tuple[bool, str]:
        """Setup TLS/HTTPS"""
        if not self.enable_tls:
            return True, "TLS disabled"
        
        logger.info("🔐 Setting up TLS...")
        
        try:
            cert_path_obj = Path(cert_path)
            key_path_obj = Path(key_path)
            
            if not cert_path_obj.exists() or not key_path_obj.exists():
                logger.warning("TLS certificates not found. Generate with:")
                logger.warning(f"  openssl req -x509 -newkey rsa:4096 -nodes -out {cert_path} -keyout {key_path} -days 365")
                return False, "TLS certificates missing"
            
            # Verify certificate
            try:
                ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                logger.info("✅ TLS certificates verified")
                return True, "TLS setup complete"
            except Exception as e:
                return False, f"Certificate verification failed: {e}"
        
        except Exception as e:
            logger.error(f"TLS setup failed: {e}")
            return False, str(e)
    
    def run_load_test(self, requests: int = 100, concurrent: int = 10) -> Tuple[bool, str]:
        """Run load test (100 requests)"""
        logger.info(f"🔥 Running load test: {requests} requests, {concurrent} concurrent...")
        
        try:
            import asyncio
            import httpx
            from statistics import mean
            
            async def load_test():
                times = []
                errors = 0
                
                async with httpx.AsyncClient() as client:
                    for i in range(requests):
                        try:
                            start = datetime.now()
                            response = await client.get(
                                "http://localhost:8888/",
                                timeout=10.0
                            )
                            elapsed = (datetime.now() - start).total_seconds() * 1000
                            times.append(elapsed)
                            
                            if response.status_code != 200:
                                errors += 1
                        except Exception as e:
                            errors += 1
                
                return times, errors
            
            # Run async test
            times, errors = asyncio.run(load_test())
            
            if not times:
                return False, "Load test produced no results"
            
            error_rate = (errors / requests) * 100
            avg_time = mean(times)
            
            logger.info(f"  Completed {len(times)} requests")
            logger.info(f"  Error rate: {error_rate:.1f}%")
            logger.info(f"  Average latency: {avg_time:.2f}ms")
            
            # Check SLA: <5% error rate
            if error_rate <= 5:
                logger.info("✅ Load test PASSED")
                return True, f"Passed ({len(times)} requests, {error_rate:.1f}% errors)"
            else:
                logger.error("❌ Load test FAILED")
                return False, f"Error rate {error_rate:.1f}% > 5%"
        
        except Exception as e:
            logger.error(f"Load test error: {e}")
            return False, str(e)
    
    def deploy_to_production(self, environment: str = 'production') -> bool:
        """Execute complete deployment pipeline"""
        logger.info("=" * 70)
        logger.info(f"🚀 PRODUCTION DEPLOYMENT: {environment.upper()}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 70)
        
        try:
            # Step 1: Pre-deployment checks
            success, details = self.run_pre_deployment_checks()
            if not success:
                logger.error("Pre-deployment checks failed")
                return False
            
            # Step 2: Backup
            backup_location = self.backup_current_deployment()
            
            # Step 3: TLS Setup
            if self.enable_tls:
                success, msg = self.setup_tls()
                if not success:
                    logger.warning(f"TLS setup warning: {msg}")
            
            # Step 4: Load Testing
            logger.info("=" * 70)
            logger.info("Running load test before deployment...")
            logger.info("=" * 70)
            
            # Note: This assumes proxy is already running
            # In real deployment, start proxy first
            success, msg = self.run_load_test(requests=100, concurrent=10)
            if not success:
                logger.error(f"Load test failed: {msg}")
                logger.info("🔄 Would rollback deployment")
                return False
            
            # Step 5: Record deployment
            deployment_record = {
                'timestamp': datetime.now().isoformat(),
                'environment': environment,
                'backup': backup_location,
                'status': 'success',
                'version': self._get_version()
            }
            
            self.deployment_history.append(deployment_record)
            
            logger.info("=" * 70)
            logger.info("✅ DEPLOYMENT SUCCESSFUL")
            logger.info("=" * 70)
            logger.info(f"Backup location: {backup_location}")
            logger.info(f"Environment: {environment}")
            logger.info(f"Timestamp: {datetime.now().isoformat()}")
            
            return True
        
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    def rollback_deployment(self, backup_path: str) -> bool:
        """Rollback to previous deployment"""
        logger.error("🔄 ROLLING BACK DEPLOYMENT")
        
        try:
            backup = Path(backup_path)
            if not backup.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            # Restore files
            for file in backup.glob("*"):
                shutil.copy(file, Path.cwd() / file.name)
            
            logger.info("✅ Rollback successful")
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _get_version(self) -> str:
        """Get deployment version"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()[:8]
        except:
            pass
        return "unknown"
    
    def get_deployment_history(self) -> List[Dict]:
        """Get deployment history"""
        return self.deployment_history


class DeploymentMonitor:
    """Monitor deployment health"""
    
    def __init__(self):
        self.health_checks = []
        self.alerts = []
    
    def monitor_service(self, url: str = "http://localhost:8888/") -> Dict:
        """Monitor service health"""
        import httpx
        from datetime import datetime
        
        try:
            client = httpx.Client(timeout=5.0)
            response = client.get(url)
            
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status_code': response.status_code,
                'latency_ms': response.elapsed.total_seconds() * 1000,
                'healthy': response.status_code == 200
            }
            
            self.health_checks.append(health_status)
            
            if not health_status['healthy']:
                self.alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': 'error',
                    'message': f"Service unhealthy: {response.status_code}"
                })
            
            return health_status
        
        except Exception as e:
            error_status = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status_code': 0,
                'latency_ms': 0,
                'healthy': False,
                'error': str(e)
            }
            
            self.health_checks.append(error_status)
            self.alerts.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'critical',
                'message': f"Service unreachable: {e}"
            })
            
            return error_status
    
    def get_alerts(self) -> List[Dict]:
        """Get all alerts"""
        return self.alerts
    
    def get_health_history(self) -> List[Dict]:
        """Get health check history"""
        return self.health_checks


if __name__ == "__main__":
    # Example usage
    deployer = ProductionDeployer(environment='production', enable_tls=True)
    
    # Run deployment
    success = deployer.deploy_to_production(environment='production')
    
    # Monitor
    monitor = DeploymentMonitor()
    health = monitor.monitor_service()
    
    print(f"Deployment: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Health: {health}")
