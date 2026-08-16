import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import uuid


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "data"

DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "computebench.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# GENERATE SESSION ID
# ============================================================

def generate_session_id():
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:4].upper()

    return f"CB-{date_part}-{random_part}"


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS benchmark_runs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            timestamp TEXT NOT NULL,

            gpu_name TEXT NOT NULL,

            cuda_version TEXT,

            matrix_size INTEGER NOT NULL,

            runs INTEGER NOT NULL,

            warmup_runs INTEGER NOT NULL,

            mean_ms REAL NOT NULL,

            median_ms REAL NOT NULL,

            minimum_ms REAL NOT NULL,

            maximum_ms REAL NOT NULL,

            std_dev_ms REAL NOT NULL,

            gflops REAL NOT NULL,

            best_gflops REAL NOT NULL,

            gpu_memory_mb REAL,

            gpu_memory_reserved_mb REAL

        )
        """
    )

    connection.commit()

    # ========================================================
    # MIGRATE OLD DATABASE
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(benchmark_runs)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if "session_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE benchmark_runs
            ADD COLUMN session_id TEXT
            """
        )

        connection.commit()

    # ========================================================
    # CREATE SESSION IDS FOR OLD RECORDS
    # ========================================================

    cursor.execute(
        """
        SELECT *
        FROM benchmark_runs
        WHERE session_id IS NULL
        ORDER BY timestamp ASC
        """
    )

    old_rows = cursor.fetchall()

    previous_timestamp = None
    current_session = None

    for row in old_rows:

        try:

            current_timestamp = datetime.fromisoformat(
                row["timestamp"]
            )

        except Exception:

            current_timestamp = datetime.now()

        if (
            previous_timestamp is None
            or abs(
                (
                    current_timestamp
                    - previous_timestamp
                ).total_seconds()
            ) > 10
        ):

            current_session = generate_session_id()

        cursor.execute(
            """
            UPDATE benchmark_runs
            SET session_id = ?
            WHERE id = ?
            """,
            (
                current_session,
                row["id"],
            ),
        )

        previous_timestamp = current_timestamp

    connection.commit()
    connection.close()


# ============================================================
# SAVE BENCHMARK RESULT
# ============================================================

def save_benchmark_result(
    session_id,
    gpu_name,
    cuda_version,
    result,
):

    connection = get_connection()
    cursor = connection.cursor()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    cursor.execute(
        """
        INSERT INTO benchmark_runs (

            session_id,
            timestamp,
            gpu_name,
            cuda_version,
            matrix_size,
            runs,
            warmup_runs,
            mean_ms,
            median_ms,
            minimum_ms,
            maximum_ms,
            std_dev_ms,
            gflops,
            best_gflops,
            gpu_memory_mb,
            gpu_memory_reserved_mb

        )

        VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?
        )
        """,
        (
            session_id,
            timestamp,
            gpu_name,
            cuda_version,
            result["matrix_size"],
            result["runs"],
            result["warmup_runs"],
            result["mean_ms"],
            result["median_ms"],
            result["minimum_ms"],
            result["maximum_ms"],
            result["std_dev_ms"],
            result["gflops"],
            result["best_gflops"],
            result.get("gpu_memory_mb"),
            result.get(
                "gpu_memory_reserved_mb"
            ),
        ),
    )

    connection.commit()
    connection.close()


# ============================================================
# GET BENCHMARK HISTORY
# ============================================================

def get_benchmark_history(limit=100):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM benchmark_runs
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET BENCHMARK SESSIONS
# ============================================================

def get_benchmark_sessions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            session_id,
            timestamp,
            gpu_name,
            cuda_version,
            matrix_size,
            runs,
            warmup_runs,
            mean_ms,
            median_ms,
            minimum_ms,
            maximum_ms,
            std_dev_ms,
            gflops,
            best_gflops,
            gpu_memory_mb,
            gpu_memory_reserved_mb
        FROM benchmark_runs
        WHERE session_id IS NOT NULL
        ORDER BY timestamp DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    grouped = {}

    for row in rows:

        session_id = row["session_id"]

        if session_id not in grouped:

            grouped[session_id] = {
                "session_id": session_id,
                "timestamp": row["timestamp"],
                "gpu_name": row["gpu_name"],
                "cuda_version": row["cuda_version"],
                "results": [],
            }

        grouped[session_id]["results"].append(
            {
                "matrix_size": row["matrix_size"],
                "runs": row["runs"],
                "warmup_runs": row["warmup_runs"],
                "mean_ms": row["mean_ms"],
                "median_ms": row["median_ms"],
                "minimum_ms": row["minimum_ms"],
                "maximum_ms": row["maximum_ms"],
                "std_dev_ms": row["std_dev_ms"],
                "gflops": row["gflops"],
                "best_gflops": row["best_gflops"],
                "gpu_memory_mb": row["gpu_memory_mb"],
                "gpu_memory_reserved_mb": row[
                    "gpu_memory_reserved_mb"
                ],
            }
        )

    return list(grouped.values())


# ============================================================
# COMPARE TWO BENCHMARK SESSIONS
# ============================================================

def compare_benchmark_sessions(
    session_a_id,
    session_b_id,
):

    sessions = get_benchmark_sessions()

    session_a = None
    session_b = None

    for session in sessions:

        if session["session_id"] == session_a_id:
            session_a = session

        if session["session_id"] == session_b_id:
            session_b = session

    if session_a is None:

        raise ValueError(
            f"Session not found: {session_a_id}"
        )

    if session_b is None:

        raise ValueError(
            f"Session not found: {session_b_id}"
        )

    if session_a_id == session_b_id:

        raise ValueError(
            "Cannot compare a session with itself."
        )

    # ========================================================
    # INDEX RESULTS BY MATRIX SIZE
    # ========================================================

    results_a = {
        result["matrix_size"]: result
        for result in session_a["results"]
    }

    results_b = {
        result["matrix_size"]: result
        for result in session_b["results"]
    }

    common_sizes = sorted(
        set(results_a.keys())
        &
        set(results_b.keys())
    )

    if not common_sizes:

        raise ValueError(
            "The two sessions have no common matrix sizes."
        )

    # ========================================================
    # COMPARE WORKLOADS
    # ========================================================

    comparisons = []

    a_wins = 0
    b_wins = 0
    ties = 0

    total_a = 0
    total_b = 0

    for matrix_size in common_sizes:

        a = results_a[matrix_size]
        b = results_b[matrix_size]

        a_gflops = float(
            a["gflops"]
        )

        b_gflops = float(
            b["gflops"]
        )

        # ----------------------------------------------------
        # Difference relative to GPU A
        # ----------------------------------------------------

        if a_gflops > 0:

            percentage_difference = (
                (
                    b_gflops
                    - a_gflops
                )
                / a_gflops
            ) * 100

        else:

            percentage_difference = 0

        # ----------------------------------------------------
        # Winner
        # ----------------------------------------------------

        if a_gflops > b_gflops:

            winner = "A"
            a_wins += 1

        elif b_gflops > a_gflops:

            winner = "B"
            b_wins += 1

        else:

            winner = "TIE"
            ties += 1

        total_a += a_gflops
        total_b += b_gflops

        comparisons.append(
            {
                "matrix_size": matrix_size,

                "gpu_a_gflops": a_gflops,

                "gpu_b_gflops": b_gflops,

                "gpu_a_best_gflops": float(
                    a["best_gflops"]
                ),

                "gpu_b_best_gflops": float(
                    b["best_gflops"]
                ),

                "gpu_a_mean_ms": float(
                    a["mean_ms"]
                ),

                "gpu_b_mean_ms": float(
                    b["mean_ms"]
                ),

                "gpu_a_std_dev_ms": float(
                    a["std_dev_ms"]
                ),

                "gpu_b_std_dev_ms": float(
                    b["std_dev_ms"]
                ),

                "percentage_difference": percentage_difference,

                "winner": winner,
            }
        )

    # ========================================================
    # OVERALL PERFORMANCE
    # ========================================================

    average_a = (
        total_a /
        len(comparisons)
    )

    average_b = (
        total_b /
        len(comparisons)
    )

    if average_a > average_b:

        overall_winner = "A"

        overall_difference = (
            (
                average_a
                - average_b
            )
            / average_b
        ) * 100

    elif average_b > average_a:

        overall_winner = "B"

        overall_difference = (
            (
                average_b
                - average_a
            )
            / average_a
        ) * 100

    else:

        overall_winner = "TIE"
        overall_difference = 0

    return {

        "gpu_a": {

            "session_id":
                session_a["session_id"],

            "name":
                session_a["gpu_name"],

            "cuda_version":
                session_a["cuda_version"],

        },

        "gpu_b": {

            "session_id":
                session_b["session_id"],

            "name":
                session_b["gpu_name"],

            "cuda_version":
                session_b["cuda_version"],

        },

        "comparisons":
            comparisons,

        "summary": {

            "gpu_a_average_gflops":
                average_a,

            "gpu_b_average_gflops":
                average_b,

            "gpu_a_wins":
                a_wins,

            "gpu_b_wins":
                b_wins,

            "ties":
                ties,

            "overall_winner":
                overall_winner,

            "overall_difference_percent":
                overall_difference,

        },
    }


# ============================================================
# IMPORT BENCHMARK DATASET
# ============================================================

def import_benchmark_dataset(
    dataset
):

    if not isinstance(
        dataset,
        dict
    ):

        raise ValueError(
            "Dataset must be a JSON object."
        )

    if (
        dataset.get("format")
        != "ComputeBench Dataset"
    ):

        raise ValueError(
            "Invalid ComputeBench dataset."
        )

    sessions = dataset.get(
        "sessions"
    )

    if not isinstance(
        sessions,
        list
    ):

        raise ValueError(
            "Dataset does not contain valid sessions."
        )

    connection = get_connection()
    cursor = connection.cursor()

    imported_count = 0

    for session in sessions:

        session_id = session.get(
            "session_id"
        )

        gpu_name = session.get(
            "gpu_name"
        )

        cuda_version = session.get(
            "cuda_version"
        )

        timestamp = session.get(
            "timestamp"
        )

        results = session.get(
            "results"
        )

        # ----------------------------------------------------
        # VALIDATE SESSION
        # ----------------------------------------------------

        if not session_id:

            raise ValueError(
                "Session is missing session_id."
            )

        if not gpu_name:

            raise ValueError(
                f"Session {session_id} "
                "is missing GPU name."
            )

        if not timestamp:

            raise ValueError(
                f"Session {session_id} "
                "is missing timestamp."
            )

        if not isinstance(
            results,
            list
        ):

            raise ValueError(
                f"Session {session_id} "
                "has invalid results."
            )

        if len(results) == 0:

            raise ValueError(
                f"Session {session_id} "
                "contains no results."
            )

        # ----------------------------------------------------
        # CHECK DUPLICATE
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM benchmark_runs
            WHERE session_id = ?
            """,
            (session_id,),
        )

        exists = cursor.fetchone()[0]

        if exists:

            continue

        # ----------------------------------------------------
        # INSERT RESULTS
        # ----------------------------------------------------

        for result in results:

            required_fields = [
                "matrix_size",
                "runs",
                "warmup_runs",
                "mean_ms",
                "median_ms",
                "minimum_ms",
                "maximum_ms",
                "std_dev_ms",
                "gflops",
                "best_gflops",
            ]

            for field in required_fields:

                if field not in result:

                    raise ValueError(
                        f"Session {session_id} "
                        f"is missing {field}."
                    )

            cursor.execute(
                """
                INSERT INTO benchmark_runs (

                    session_id,
                    timestamp,
                    gpu_name,
                    cuda_version,
                    matrix_size,
                    runs,
                    warmup_runs,
                    mean_ms,
                    median_ms,
                    minimum_ms,
                    maximum_ms,
                    std_dev_ms,
                    gflops,
                    best_gflops,
                    gpu_memory_mb,
                    gpu_memory_reserved_mb

                )

                VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?
                )
                """,
                (
                    session_id,
                    timestamp,
                    gpu_name,
                    cuda_version,
                    result["matrix_size"],
                    result["runs"],
                    result["warmup_runs"],
                    result["mean_ms"],
                    result["median_ms"],
                    result["minimum_ms"],
                    result["maximum_ms"],
                    result["std_dev_ms"],
                    result["gflops"],
                    result["best_gflops"],
                    result.get(
                        "gpu_memory_mb"
                    ),
                    result.get(
                        "gpu_memory_reserved_mb"
                    ),
                ),
            )

        imported_count += 1

    connection.commit()
    connection.close()

    return imported_count


# ============================================================
# CLEAR HISTORY
# ============================================================

def clear_benchmark_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM benchmark_runs"
    )

    connection.commit()
    connection.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()