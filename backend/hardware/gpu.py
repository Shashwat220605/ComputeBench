import torch


def get_gpu_info():
    if not torch.cuda.is_available():
        return {
            "available": False,
            "name": None,
            "cuda_version": None,
            "vram_gb": None,
        }

    gpu = torch.cuda.get_device_properties(0)

    return {
        "available": True,
        "name": gpu.name,
        "cuda_version": torch.version.cuda,
        "vram_gb": round(gpu.total_memory / (1024 ** 3), 2),
    }


if __name__ == "__main__":
    info = get_gpu_info()

    print("=== GPU Information ===")

    for key, value in info.items():
        print(f"{key}: {value}")