"""
Compliance Scan Engine Performance Benchmark
Measures scan performance with different dataset sizes
"""
import requests
import time
import psutil
import os
import sys
from typing import Dict, Any
import json

API_BASE = "http://localhost:8000"

class ScanBenchmark:
    def __init__(self, token: str, dataset_file: str):
        self.token = token
        self.dataset_file = dataset_file
        self.results = {}
        
    def get_file_size_mb(self) -> float:
        """Get dataset file size in MB"""
        size_bytes = os.path.getsize(self.dataset_file)
        return round(size_bytes / (1024 * 1024), 2)
        
    def count_transactions(self) -> int:
        """Count transactions in dataset"""
        with open(self.dataset_file, 'r') as f:
            return sum(1 for line in f) - 1  # Subtract header
            
    def measure_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": round(memory_info.rss / (1024 * 1024), 2),
            "vms_mb": round(memory_info.vms / (1024 * 1024), 2),
            "percent": round(process.memory_percent(), 2)
        }
        
    def measure_cpu_usage(self) -> float:
        """Get current CPU usage"""
        return psutil.cpu_percent(interval=1)
        
    def upload_dataset(self) -> bool:
        """Upload dataset as connector"""
        print("Uploading dataset...")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Add CSV connector
            response = requests.post(
                f"{API_BASE}/api/connectors/add",
                headers=headers,
                json={
                    "connector_type": "csv",
                    "name": "Benchmark Dataset",
                    "config": {
                        "file_path": self.dataset_file
                    }
                }
            )
            
            if response.status_code != 200:
                print(f"Failed to add connector: {response.text}")
                return False
                
            self.connector_id = response.json().get("connector_id")
            print(f"✓ Dataset uploaded. Connector ID: {self.connector_id}")
            return True
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return False
            
    def run_scan_benchmark(self) -> Dict[str, Any]:
        """Run compliance scan and measure performance"""
        print("\nStarting compliance scan benchmark...")
        
        # Measure initial state
        initial_memory = self.measure_memory_usage()
        initial_cpu = self.measure_cpu_usage()
        
        # Start scan
        headers = {'Authorization': f'Bearer {self.token}'}
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE}/api/compliance/scan",
                headers=headers,
                json={
                    "connector_id": self.connector_id,
                    "limit": 1000000  # No limit
                },
                timeout=600  # 10 minute timeout
            )
            
            end_time = time.time()
            
            if response.status_code != 200:
                print(f"Scan failed: {response.text}")
                return {}
                
            scan_result = response.json()
            
            # Measure final state
            final_memory = self.measure_memory_usage()
            final_cpu = self.measure_cpu_usage()
            
            # Calculate metrics
            total_time = end_time - start_time
            transactions_scanned = scan_result.get("transactions_scanned", 0)
            violations_detected = scan_result.get("violations_detected", 0)
            
            throughput = transactions_scanned / total_time if total_time > 0 else 0
            
            memory_delta = final_memory["rss_mb"] - initial_memory["rss_mb"]
            
            results = {
                "dataset_file": self.dataset_file,
                "file_size_mb": self.get_file_size_mb(),
                "total_transactions": transactions_scanned,
                "violations_detected": violations_detected,
                "performance": {
                    "total_time_seconds": round(total_time, 2),
                    "throughput_per_second": round(throughput, 2),
                    "time_per_transaction_ms": round((total_time / transactions_scanned) * 1000, 3) if transactions_scanned > 0 else 0
                },
                "memory": {
                    "initial_mb": initial_memory["rss_mb"],
                    "final_mb": final_memory["rss_mb"],
                    "delta_mb": round(memory_delta, 2),
                    "peak_percent": max(initial_memory["percent"], final_memory["percent"])
                },
                "cpu": {
                    "initial_percent": initial_cpu,
                    "final_percent": final_cpu,
                    "average_percent": round((initial_cpu + final_cpu) / 2, 2)
                },
                "compliance_rate": scan_result.get("compliance_rate", 0)
            }
            
            self.results = results
            return results
            
        except requests.exceptions.Timeout:
            print("Scan timed out after 10 minutes")
            return {}
        except Exception as e:
            print(f"Benchmark error: {str(e)}")
            return {}
            
    def print_results(self):
        """Print benchmark results"""
        if not self.results:
            print("No results to display")
            return
            
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        
        print(f"\nDataset:")
        print(f"  File: {self.results['dataset_file']}")
        print(f"  Size: {self.results['file_size_mb']} MB")
        print(f"  Transactions: {self.results['total_transactions']:,}")
        print(f"  Violations: {self.results['violations_detected']:,}")
        
        perf = self.results['performance']
        print(f"\nPerformance:")
        print(f"  Total Time: {perf['total_time_seconds']} seconds")
        print(f"  Throughput: {perf['throughput_per_second']:,.0f} transactions/second")
        print(f"  Time per Transaction: {perf['time_per_transaction_ms']} ms")
        
        mem = self.results['memory']
        print(f"\nMemory Usage:")
        print(f"  Initial: {mem['initial_mb']} MB")
        print(f"  Final: {mem['final_mb']} MB")
        print(f"  Delta: {mem['delta_mb']} MB")
        print(f"  Peak: {mem['peak_percent']}%")
        
        cpu = self.results['cpu']
        print(f"\nCPU Usage:")
        print(f"  Average: {cpu['average_percent']}%")
        
        print(f"\nCompliance Rate: {self.results['compliance_rate']}%")
        
        # Performance assessment
        print("\n" + "=" * 60)
        print("PERFORMANCE ASSESSMENT")
        print("=" * 60)
        
        if perf['total_time_seconds'] > 10 and self.results['total_transactions'] >= 100000:
            print("⚠ WARNING: Scan time exceeds 10 seconds for 100k+ transactions")
            print("  Recommendations:")
            print("  - Implement batch processing (chunk size 10k)")
            print("  - Add database indexes on transaction_id, org_id, rule_id")
            print("  - Consider async background workers")
        else:
            print("✓ Performance within acceptable range")
            
        if mem['delta_mb'] > 500:
            print("⚠ WARNING: High memory consumption")
            print("  Recommendations:")
            print("  - Implement streaming processing")
            print("  - Reduce batch size")
            print("  - Add memory limits")
        else:
            print("✓ Memory usage acceptable")
            
    def save_results(self, output_file: str = "benchmark_results.json"):
        """Save results to JSON file"""
        if not self.results:
            return
            
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\n✓ Results saved to {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark compliance scan engine')
    parser.add_argument('dataset', type=str, help='Path to transaction dataset CSV')
    parser.add_argument('--token', type=str, required=True, help='API authentication token')
    parser.add_argument('--output', type=str, default='benchmark_results.json', help='Output file for results')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"Error: Dataset file not found: {args.dataset}")
        sys.exit(1)
        
    benchmark = ScanBenchmark(args.token, args.dataset)
    
    if not benchmark.upload_dataset():
        sys.exit(1)
        
    results = benchmark.run_scan_benchmark()
    
    if results:
        benchmark.print_results()
        benchmark.save_results(args.output)
    else:
        print("Benchmark failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
