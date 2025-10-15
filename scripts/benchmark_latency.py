"""Benchmark script for measuring system latency."""
import time
import statistics
from typing import List, Dict
import requests


class LatencyBenchmark:
    """Benchmark tool for measuring system latency."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize benchmark tool.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.token = None

    def login(self, access_key: str) -> bool:
        """Login and get authentication token."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"access_key": access_key}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                return True
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def benchmark_query(self, query: str, num_runs: int = 10) -> Dict:
        """
        Benchmark query latency.

        Args:
            query: Query to benchmark
            num_runs: Number of runs

        Returns:
            Benchmark results
        """
        if not self.token:
            return {"error": "Not authenticated"}

        latencies = []
        headers = {"Authorization": f"Bearer {self.token}"}

        print(f"\nRunning {num_runs} query benchmarks...")

        for i in range(num_runs):
            start_time = time.time()

            try:
                response = requests.post(
                    f"{self.base_url}/query",
                    headers=headers,
                    json={"query": query, "conversation_history": []},
                    timeout=30
                )

                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to ms

                if response.status_code == 200:
                    latencies.append(latency)
                    print(f"Run {i+1}: {latency:.2f}ms")
                else:
                    print(f"Run {i+1}: Failed with status {response.status_code}")

            except Exception as e:
                print(f"Run {i+1}: Error - {str(e)}")

        if not latencies:
            return {"error": "No successful runs"}

        return {
            "num_runs": len(latencies),
            "mean_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "stdev_latency_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)]
        }


def main():
    """Main benchmark execution."""
    print("=" * 60)
    print("AI Voice Knowledge Assistant - Latency Benchmark")
    print("=" * 60)

    benchmark = LatencyBenchmark()

    # Login
    print("\nAuthenticating...")
    if not benchmark.login("admin_hasan_007_no_exit"):
        print("Authentication failed!")
        return

    print("Authentication successful!")

    # Run benchmarks
    test_query = "What is artificial intelligence?"
    results = benchmark.benchmark_query(test_query, num_runs=10)

    if "error" in results:
        print(f"\nBenchmark failed: {results['error']}")
        return

    # Print results
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Number of runs:     {results['num_runs']}")
    print(f"Mean latency:       {results['mean_latency_ms']:.2f}ms")
    print(f"Median latency:     {results['median_latency_ms']:.2f}ms")
    print(f"Min latency:        {results['min_latency_ms']:.2f}ms")
    print(f"Max latency:        {results['max_latency_ms']:.2f}ms")
    print(f"Std deviation:      {results['stdev_latency_ms']:.2f}ms")
    print(f"95th percentile:    {results['p95_latency_ms']:.2f}ms")
    print("=" * 60)


if __name__ == "__main__":
    main()
