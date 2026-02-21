"""
API Performance Monitoring Middleware
Tracks request execution time, slow queries, and memory usage
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
import psutil
from typing import Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Performance thresholds
SLOW_REQUEST_THRESHOLD = 0.2  # 200ms
MEMORY_WARNING_THRESHOLD = 80  # 80% memory usage

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor API performance and log slow requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip monitoring for health checks and metrics endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
            
        # Record start time and memory
        start_time = time.time()
        process = psutil.Process()
        start_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        end_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_delta = end_memory - start_memory
        memory_percent = process.memory_percent()
        
        # Log slow requests
        if duration > SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.url.path} "
                f"took {duration:.3f}s (threshold: {SLOW_REQUEST_THRESHOLD}s)"
            )
            
        # Log memory spikes
        if memory_percent > MEMORY_WARNING_THRESHOLD:
            logger.warning(
                f"HIGH MEMORY: {request.method} {request.url.path} "
                f"memory at {memory_percent:.1f}% (threshold: {MEMORY_WARNING_THRESHOLD}%)"
            )
            
        # Log significant memory increases
        if memory_delta > 50:  # 50MB increase
            logger.warning(
                f"MEMORY SPIKE: {request.method} {request.url.path} "
                f"increased memory by {memory_delta:.1f}MB"
            )
            
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Memory-Delta"] = f"{memory_delta:.2f}MB"
        
        # Log all requests (INFO level)
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration:.3f}s "
            f"memory_delta={memory_delta:.2f}MB"
        )
        
        return response


# Metrics storage (in-memory for now, should use Redis in production)
class PerformanceMetrics:
    """Store and retrieve performance metrics"""
    
    def __init__(self):
        self.requests = []
        self.slow_queries = []
        self.max_requests = 1000  # Keep last 1000 requests
        
    def add_request(self, method: str, path: str, duration: float, status_code: int):
        """Add request metrics"""
        self.requests.append({
            "method": method,
            "path": path,
            "duration": duration,
            "status_code": status_code,
            "timestamp": time.time()
        })
        
        # Keep only recent requests
        if len(self.requests) > self.max_requests:
            self.requests = self.requests[-self.max_requests:]
            
        # Track slow queries
        if duration > SLOW_REQUEST_THRESHOLD:
            self.slow_queries.append({
                "method": method,
                "path": path,
                "duration": duration,
                "timestamp": time.time()
            })
            
    def get_summary(self) -> dict:
        """Get performance summary"""
        if not self.requests:
            return {
                "total_requests": 0,
                "average_duration": 0,
                "slow_requests": 0,
                "p95_duration": 0,
                "p99_duration": 0
            }
            
        durations = [r["duration"] for r in self.requests]
        durations.sort()
        
        total = len(durations)
        p95_index = int(total * 0.95)
        p99_index = int(total * 0.99)
        
        return {
            "total_requests": total,
            "average_duration": round(sum(durations) / total, 3),
            "slow_requests": len(self.slow_queries),
            "p95_duration": round(durations[p95_index] if p95_index < total else 0, 3),
            "p99_duration": round(durations[p99_index] if p99_index < total else 0, 3),
            "slowest_endpoints": self._get_slowest_endpoints()
        }
        
    def _get_slowest_endpoints(self, limit: int = 5) -> list:
        """Get slowest endpoints"""
        endpoint_times = {}
        
        for req in self.requests:
            path = req["path"]
            if path not in endpoint_times:
                endpoint_times[path] = []
            endpoint_times[path].append(req["duration"])
            
        # Calculate average per endpoint
        endpoint_averages = [
            {
                "path": path,
                "average_duration": round(sum(times) / len(times), 3),
                "request_count": len(times)
            }
            for path, times in endpoint_times.items()
        ]
        
        # Sort by average duration
        endpoint_averages.sort(key=lambda x: x["average_duration"], reverse=True)
        
        return endpoint_averages[:limit]


# Global metrics instance
performance_metrics = PerformanceMetrics()
