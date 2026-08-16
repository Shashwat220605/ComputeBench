import statistics
import torch


# ============================================================
# Configuration
# ============================================================

DEFAULT_MATRIX_SIZES = [512, 1024, 2048, 4096]

DEFAULT_WARMUP_RUNS = 3

DEFAULT_BENCHMARK_RUNS = 10


# ============================================================
# Single Matrix Multiplication Measurement
# ============================================================

def measure_matrix_multiplication(
    a: torch.Tensor,
    b: torch.Tensor,
) -> float:
    """
    Measure one GPU matrix multiplication.

    Returns:
        Execution time in milliseconds.
    """

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()

    torch.matmul(a, b)

    end.record()

    # CUDA operations are asynchronous.
    # Synchronization ensures the GPU has finished
    # before we read the timing result.
    torch.cuda.synchronize()

    return start.elapsed_time(end)


# ============================================================
# Matrix Multiplication Benchmark
# ============================================================

def benchmark_matrix_multiplication(
    size: int,
    warmup_runs: int = DEFAULT_WARMUP_RUNS,
    benchmark_runs: int = DEFAULT_BENCHMARK_RUNS,
):
    """
    Benchmark matrix multiplication using repeated measurements.

    Returns:
        Dictionary containing benchmark statistics.
    """

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is not available.")

    device = torch.device("cuda")

    # --------------------------------------------------------
    # Create matrices directly on the GPU
    # --------------------------------------------------------

    a = torch.randn(
        size,
        size,
        device=device,
        dtype=torch.float32,
    )

    b = torch.randn(
        size,
        size,
        device=device,
        dtype=torch.float32,
    )

    # --------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------

    for _ in range(warmup_runs):
        torch.matmul(a, b)

    torch.cuda.synchronize()

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    execution_times = []

    for _ in range(benchmark_runs):

        elapsed_ms = measure_matrix_multiplication(a, b)

        execution_times.append(elapsed_ms)

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    mean_ms = statistics.mean(execution_times)

    median_ms = statistics.median(execution_times)

    minimum_ms = min(execution_times)

    maximum_ms = max(execution_times)

    if len(execution_times) > 1:
        std_dev_ms = statistics.stdev(execution_times)
    else:
        std_dev_ms = 0.0

    # --------------------------------------------------------
    # GFLOPS
    # --------------------------------------------------------
    #
    # Matrix multiplication:
    #
    # C = A × B
    #
    # Approximate floating-point operations:
    #
    # 2 × N³
    #
    # --------------------------------------------------------

    operations = 2 * (size ** 3)

    mean_gflops = (
        operations
        / (mean_ms / 1000)
        / 1e9
    )

    best_gflops = (
        operations
        / (minimum_ms / 1000)
        / 1e9
    )

    # --------------------------------------------------------
    # GPU memory
    # --------------------------------------------------------

    memory_allocated_mb = (
        torch.cuda.memory_allocated()
        / (1024 ** 2)
    )

    memory_reserved_mb = (
        torch.cuda.memory_reserved()
        / (1024 ** 2)
    )

    # --------------------------------------------------------
    # Clean up
    # --------------------------------------------------------

    del a
    del b

    torch.cuda.empty_cache()

    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {
        "workload": "matrix_multiplication",

        "matrix_size": size,

        "runs": benchmark_runs,

        "warmup_runs": warmup_runs,

        "execution_time_ms": round(mean_ms, 3),

        "mean_ms": round(mean_ms, 3),

        "median_ms": round(median_ms, 3),

        "minimum_ms": round(minimum_ms, 3),

        "maximum_ms": round(maximum_ms, 3),

        "std_dev_ms": round(std_dev_ms, 3),

        "gflops": round(mean_gflops, 2),

        "best_gflops": round(best_gflops, 2),

        "gpu_memory_mb": round(
            memory_allocated_mb,
            2,
        ),

        "gpu_memory_reserved_mb": round(
            memory_reserved_mb,
            2,
        ),

        "raw_times_ms": [
            round(time, 3)
            for time in execution_times
        ],
    }


# ============================================================
# Complete GPU Benchmark Suite
# ============================================================

def run_gpu_benchmark(
    sizes=None,
    warmup_runs=DEFAULT_WARMUP_RUNS,
    benchmark_runs=DEFAULT_BENCHMARK_RUNS,
):
    """
    Run the complete GPU benchmark suite.

    Returns:
        List of benchmark results.
    """

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is not available.")

    if sizes is None:
        sizes = DEFAULT_MATRIX_SIZES

    results = []

    for size in sizes:

        print(
            f"Running {size} × {size} "
            f"matrix benchmark..."
        )

        result = benchmark_matrix_multiplication(
            size=size,
            warmup_runs=warmup_runs,
            benchmark_runs=benchmark_runs,
        )

        results.append(result)

    return results


# ============================================================
# Console Output
# ============================================================

def print_results(results):
    """
    Print benchmark results in a readable format.
    """

    print("\n")
    print("=" * 90)
    print("                     COMPUTEBENCH")
    print("                  GPU BENCHMARK RESULTS")
    print("=" * 90)

    print()

    for result in results:

        print(
            f"Matrix Size : "
            f"{result['matrix_size']} × "
            f"{result['matrix_size']}"
        )

        print(
            f"Runs        : "
            f"{result['runs']}"
        )

        print(
            f"Mean        : "
            f"{result['mean_ms']:.3f} ms"
        )

        print(
            f"Median      : "
            f"{result['median_ms']:.3f} ms"
        )

        print(
            f"Best        : "
            f"{result['minimum_ms']:.3f} ms"
        )

        print(
            f"Worst       : "
            f"{result['maximum_ms']:.3f} ms"
        )

        print(
            f"Std Dev     : "
            f"{result['std_dev_ms']:.3f} ms"
        )

        print(
            f"Performance : "
            f"{result['gflops']:.2f} GFLOPS"
        )

        print(
            f"Best GFLOPS : "
            f"{result['best_gflops']:.2f}"
        )

        print(
            f"VRAM Used   : "
            f"{result['gpu_memory_mb']:.2f} MB"
        )

        print("-" * 90)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("Starting ComputeBench GPU benchmark...")
    print()

    if not torch.cuda.is_available():

        print("ERROR: CUDA GPU not available.")

        exit(1)

    print(
        f"GPU: "
        f"{torch.cuda.get_device_name(0)}"
    )

    print(
        f"CUDA: "
        f"{torch.version.cuda}"
    )

    properties = torch.cuda.get_device_properties(0)

    total_vram_gb = (
        properties.total_memory
        / (1024 ** 3)
    )

    print(
        f"VRAM: "
        f"{total_vram_gb:.2f} GB"
    )

    print()

    results = run_gpu_benchmark()

    print_results(results)

    print()
    print("Benchmark complete.")