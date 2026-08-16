import torch

print("=== ComputeBench GPU Benchmark ===\n")

device = torch.device("cuda")

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"CUDA: {torch.version.cuda}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

sizes = [512, 1024, 2048, 4096]

print("\nMatrix Multiplication Benchmark")
print("-" * 45)

for size in sizes:

    # Create matrices on GPU
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)

    # Warm-up
    for _ in range(3):
        torch.matmul(a, b)

    torch.cuda.synchronize()

    # GPU events
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()

    c = torch.matmul(a, b)

    end.record()

    # Wait for GPU to finish
    torch.cuda.synchronize()

    elapsed_ms = start.elapsed_time(end)

    # Calculate approximate FP32 operations
    operations = 2 * (size ** 3)

    # GFLOPS
    gflops = operations / (elapsed_ms / 1000) / 1e9

    memory = torch.cuda.memory_allocated() / 1024**2

    print(
        f"{size:5} × {size:<5} | "
        f"{elapsed_ms:8.3f} ms | "
        f"{gflops:8.2f} GFLOPS | "
        f"{memory:7.1f} MB"
    )

    del a, b, c
    torch.cuda.empty_cache()

print("\nBenchmark complete 🚀")