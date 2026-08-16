from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# EXISTING COMPUTEBENCH IMPORTS
# ============================================================

from backend.hardware.gpu import get_gpu_info

from backend.hardware.telemetry import get_gpu_telemetry

from backend.benchmarks.gpu_benchmark import run_gpu_benchmark

from backend.database import (
    generate_session_id,
    save_benchmark_result,
    get_benchmark_history,
    clear_benchmark_history,
    import_benchmark_dataset,
    get_benchmark_sessions,
    compare_benchmark_sessions,
)


# ============================================================
# GEMINI
# ============================================================

from backend.ai.gemini import analyze_gpu_comparison


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="ComputeBench API",
    description=(
        "GPU benchmarking, telemetry, "
        "comparison and AI analysis platform"
    ),
    version="0.6.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "ComputeBench",
        "status": "running",
        "version": "0.6.0",
    }


# ============================================================
# GPU INFORMATION
# ============================================================

@app.get("/api/hardware/gpu")
def gpu_info():

    try:

        return get_gpu_info()

    except Exception as error:

        print("GPU info error:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve GPU information.",
        )


# ============================================================
# GPU TELEMETRY
# ============================================================

@app.get("/api/hardware/gpu/telemetry")
def gpu_telemetry():

    try:

        return get_gpu_telemetry()

    except Exception as error:

        print("Telemetry error:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve GPU telemetry.",
        )


# ============================================================
# RUN GPU BENCHMARK
# ============================================================

@app.post("/api/benchmark/gpu")
def gpu_benchmark():

    try:

        gpu = get_gpu_info()

        if not gpu.get("available", False):

            return {
                "success": False,
                "error": "CUDA GPU not available",
            }


        session_id = generate_session_id()


        results = run_gpu_benchmark()


        for result in results:

            save_benchmark_result(

                session_id=session_id,

                gpu_name=gpu.get(
                    "name",
                    "Unknown GPU"
                ),

                cuda_version=gpu.get(
                    "cuda_version"
                ),

                result=result,

            )


        return {
            "success": True,

            "session_id":
                session_id,

            "gpu":
                gpu,

            "results":
                results,
        }


    except Exception as error:

        print(
            "Benchmark error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Benchmark failed: {error}"
            ),
        )


# ============================================================
# BENCHMARK HISTORY
# ============================================================

@app.get("/api/benchmark/history")
def benchmark_history():

    try:

        history = get_benchmark_history()


        return {
            "success": True,

            "count":
                len(history),

            "history":
                history,
        }


    except Exception as error:

        print(
            "History error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve "
                "benchmark history."
            ),
        )


# ============================================================
# BENCHMARK SESSIONS
# ============================================================

@app.get("/api/benchmark/sessions")
def benchmark_sessions():

    try:

        sessions = get_benchmark_sessions()


        return {
            "success": True,

            "count":
                len(sessions),

            "sessions":
                sessions,
        }


    except Exception as error:

        print(
            "Sessions error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve "
                "benchmark sessions."
            ),
        )


# ============================================================
# GPU VS GPU COMPARISON
# ============================================================

@app.post("/api/benchmark/compare")
def compare_benchmarks(
    payload: dict
):

    session_a = payload.get(
        "session_a"
    )

    session_b = payload.get(
        "session_b"
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not session_a:

        raise HTTPException(
            status_code=400,
            detail=(
                "session_a is required."
            ),
        )


    if not session_b:

        raise HTTPException(
            status_code=400,
            detail=(
                "session_b is required."
            ),
        )


    if session_a == session_b:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please select two "
                "different sessions."
            ),
        )


    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    try:

        comparison = compare_benchmark_sessions(

            session_a_id=session_a,

            session_b_id=session_b,

        )


        return {
            "success": True,

            "comparison":
                comparison,
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        print(
            "Comparison error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to compare "
                "benchmark sessions."
            ),
        )


# ============================================================
# GEMINI AI ANALYSIS
# ============================================================

@app.post("/api/benchmark/ai-analysis")
def benchmark_ai_analysis(
    payload: dict
):

    comparison = payload.get(
        "comparison"
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not comparison:

        raise HTTPException(
            status_code=400,
            detail=(
                "comparison data is required."
            ),
        )


    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    try:

        result = analyze_gpu_comparison(
            comparison
        )


        return {
            "success": True,

            "analysis":
                result["analysis"],

            "model":
                result["model"],
        }


    except RuntimeError as error:

        print(
            "Gemini configuration error:",
            error
        )

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


    except Exception as error:

        print(
            "Gemini error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Gemini analysis failed: "
                f"{error}"
            ),
        )


# ============================================================
# IMPORT DATASET
# ============================================================

@app.post("/api/benchmark/import")
def import_dataset(
    dataset: dict
):

    try:

        imported_count = (
            import_benchmark_dataset(
                dataset
            )
        )


        return {
            "success": True,

            "imported_sessions":
                imported_count,

            "message": (
                f"Imported "
                f"{imported_count} "
                f"benchmark session(s)."
            ),
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        print(
            "Import error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to import "
                "dataset."
            ),
        )


# ============================================================
# CLEAR BENCHMARK HISTORY
# ============================================================

@app.delete("/api/benchmark/history")
def delete_benchmark_history():

    try:

        clear_benchmark_history()


        return {
            "success": True,

            "message":
                "Benchmark history cleared",
        }


    except Exception as error:

        print(
            "Clear history error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to clear "
                "benchmark history."
            ),
        )