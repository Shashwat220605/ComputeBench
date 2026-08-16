import pynvml


def initialize_nvml():
    try:
        pynvml.nvmlInit()
        return True
    except Exception:
        return False


def shutdown_nvml():
    try:
        pynvml.nvmlShutdown()
    except Exception:
        pass


def get_gpu_telemetry(index: int = 0):
    """
    Get live telemetry for an NVIDIA GPU.
    """

    if not initialize_nvml():
        return {
            "available": False,
            "error": "NVIDIA NVML could not be initialized",
        }

    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(index)

        name = pynvml.nvmlDeviceGetName(handle)

        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

        temperature = pynvml.nvmlDeviceGetTemperature(
            handle,
            pynvml.NVML_TEMPERATURE_GPU,
        )

        try:
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
        except pynvml.NVMLError:
            power = None

        try:
            clock_graphics = pynvml.nvmlDeviceGetClockInfo(
                handle,
                pynvml.NVML_CLOCK_GRAPHICS,
            )
        except pynvml.NVMLError:
            clock_graphics = None

        return {
            "available": True,
            "name": name,
            "gpu_utilization_percent": utilization.gpu,
            "memory_utilization_percent": utilization.memory,
            "vram_used_mb": round(memory.used / 1024**2, 2),
            "vram_total_mb": round(memory.total / 1024**2, 2),
            "vram_free_mb": round(memory.free / 1024**2, 2),
            "temperature_c": temperature,
            "power_w": round(power, 2) if power is not None else None,
            "graphics_clock_mhz": clock_graphics,
        }

    except Exception as error:
        return {
            "available": False,
            "error": str(error),
        }

    finally:
        shutdown_nvml()