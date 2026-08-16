import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";


const API_URL =
  "http://127.0.0.1:8000";


function App() {

  // =========================================================
  // GPU
  // =========================================================

  const [gpu, setGpu] =
    useState(null);

  const [telemetry, setTelemetry] =
    useState(null);


  // =========================================================
  // BENCHMARK
  // =========================================================

  const [results, setResults] =
    useState([]);

  const [runningBenchmark, setRunningBenchmark] =
    useState(false);


  // =========================================================
  // HISTORY
  // =========================================================

  const [history, setHistory] =
    useState([]);

  const [loadingHistory, setLoadingHistory] =
    useState(true);


  // =========================================================
  // SESSIONS
  // =========================================================

  const [sessions, setSessions] =
    useState([]);

  const [loadingSessions, setLoadingSessions] =
    useState(true);


  // =========================================================
  // COMPARISON
  // =========================================================

  const [sessionA, setSessionA] =
    useState("");

  const [sessionB, setSessionB] =
    useState("");

  const [comparison, setComparison] =
    useState(null);

  const [comparing, setComparing] =
    useState(false);

  const [comparisonError, setComparisonError] =
    useState(null);


  // =========================================================
  // GEMINI
  // =========================================================

  const [aiAnalysis, setAiAnalysis] =
    useState(null);

  const [aiLoading, setAiLoading] =
    useState(false);

  const [aiError, setAiError] =
    useState(null);


  // =========================================================
  // GENERAL
  // =========================================================

  const [error, setError] =
    useState(null);


  // =========================================================
  // FETCH GPU
  // =========================================================

  const fetchGpuInfo =
    async () => {

      try {

        const response =
          await fetch(
            `${API_URL}/api/hardware/gpu`
          );


        if (!response.ok) {

          throw new Error(
            "Failed to fetch GPU information."
          );

        }


        const data =
          await response.json();


        setGpu(data);


      } catch (error) {

        console.error(
          "GPU error:",
          error
        );

        setError(
          error.message
        );

      }

    };


  // =========================================================
  // TELEMETRY
  // =========================================================

  useEffect(() => {

    fetchGpuInfo();


    const fetchTelemetry =
      async () => {

        try {

          const response =
            await fetch(
              `${API_URL}/api/hardware/gpu/telemetry`
            );


          if (!response.ok) {
            return;
          }


          const data =
            await response.json();


          setTelemetry(data);


        } catch (error) {

          console.error(
            "Telemetry error:",
            error
          );

        }

      };


    fetchTelemetry();


    const interval =
      setInterval(
        fetchTelemetry,
        1000
      );


    return () => {

      clearInterval(
        interval
      );

    };

  }, []);


  // =========================================================
  // HISTORY
  // =========================================================

  const fetchHistory =
    async () => {

      try {

        setLoadingHistory(
          true
        );


        const response =
          await fetch(
            `${API_URL}/api/benchmark/history`
          );


        if (!response.ok) {

          throw new Error(
            "Failed to fetch history."
          );

        }


        const data =
          await response.json();


        setHistory(
          data.history || []
        );


      } catch (error) {

        console.error(
          "History error:",
          error
        );


      } finally {

        setLoadingHistory(
          false
        );

      }

    };


  // =========================================================
  // SESSIONS
  // =========================================================

  const fetchSessions =
    async () => {

      try {

        setLoadingSessions(
          true
        );


        const response =
          await fetch(
            `${API_URL}/api/benchmark/sessions`
          );


        if (!response.ok) {

          throw new Error(
            "Failed to fetch sessions."
          );

        }


        const data =
          await response.json();


        setSessions(
          data.sessions || []
        );


      } catch (error) {

        console.error(
          "Sessions error:",
          error
        );


      } finally {

        setLoadingSessions(
          false
        );

      }

    };


  useEffect(() => {

    fetchHistory();

    fetchSessions();

  }, []);


  // =========================================================
  // RUN BENCHMARK
  // =========================================================

  const runBenchmark =
    async () => {

      setRunningBenchmark(
        true
      );

      setError(null);

      setResults([]);


      try {

        const response =
          await fetch(
            `${API_URL}/api/benchmark/gpu`,
            {
              method: "POST",
            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            data.detail ||
            "Benchmark request failed."
          );

        }


        if (!data.success) {

          throw new Error(
            data.error ||
            "Benchmark failed."
          );

        }


        setGpu(
          data.gpu
        );


        setResults(
          data.results || []
        );


        await fetchHistory();

        await fetchSessions();


      } catch (error) {

        console.error(
          "Benchmark error:",
          error
        );


        setError(
          error.message
        );


      } finally {

        setRunningBenchmark(
          false
        );

      }

    };


  // =========================================================
  // FORMAT NUMBER
  // =========================================================

  const formatNumber =
    (
      value,
      decimals = 2
    ) => {

      if (
        value === null ||
        value === undefined ||
        Number.isNaN(
          Number(value)
        )
      ) {

        return "--";

      }


      return Number(
        value
      ).toFixed(
        decimals
      );

    };


  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate =
    timestamp => {

      if (!timestamp) {
        return "--";
      }


      try {

        return new Date(
          timestamp
        ).toLocaleString(
          undefined,
          {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          }
        );

      } catch {

        return timestamp;

      }

    };


  // =========================================================
  // SUMMARY
  // =========================================================

  const summary =
    useMemo(() => {

      if (!results.length) {
        return null;
      }


      const averageGflops =
        results.reduce(
          (
            total,
            result
          ) =>
            total +
            Number(
              result.gflops || 0
            ),
          0
        ) /
        results.length;


      const peakGflops =
        Math.max(
          ...results.map(
            result =>
              Number(
                result.best_gflops || 0
              )
          )
        );


      const fastest =
        results.reduce(
          (
            best,
            current
          ) =>
            Number(
              current.minimum_ms
            ) <
            Number(
              best.minimum_ms
            )
              ? current
              : best
        );


      const totalRuns =
        results.reduce(
          (
            total,
            result
          ) =>
            total +
            Number(
              result.runs || 0
            ),
          0
        );


      return {

        averageGflops,

        peakGflops,

        fastestMatrix:
          fastest?.matrix_size,

        totalRuns,

      };

    }, [results]);


  // =========================================================
  // HISTORY GROUPING
  // =========================================================

  const historySessions =
    useMemo(() => {

      const grouped = {};


      history.forEach(
        item => {

          const id =
            item.session_id ||
            `legacy-${item.timestamp}`;


          if (!grouped[id]) {

            grouped[id] = {

              session_id:
                id,

              timestamp:
                item.timestamp,

              gpu_name:
                item.gpu_name,

              cuda_version:
                item.cuda_version,

              results: [],

            };

          }


          grouped[id]
            .results
            .push(item);

        }
      );


      return Object.values(
        grouped
      ).sort(
        (
          a,
          b
        ) =>
          new Date(
            b.timestamp
          ) -
          new Date(
            a.timestamp
          )
      );

    }, [history]);


  // =========================================================
  // GPU COMPARISON
  // =========================================================

  const runComparison =
    async () => {

      if (!sessionA || !sessionB) {

        setComparisonError(
          "Please select two GPU sessions."
        );

        return;

      }


      if (
        sessionA === sessionB
      ) {

        setComparisonError(
          "Please select two different sessions."
        );

        return;

      }


      setComparing(
        true
      );

      setComparisonError(
        null
      );

      setComparison(
        null
      );

      setAiAnalysis(
        null
      );

      setAiError(
        null
      );


      try {

        const response =
          await fetch(
            `${API_URL}/api/benchmark/compare`,
            {

              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({

                  session_a:
                    sessionA,

                  session_b:
                    sessionB,

                }),

            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            data.detail ||
            "Comparison failed."
          );

        }


        if (!data.success) {

          throw new Error(
            "Comparison failed."
          );

        }


        setComparison(
          data.comparison
        );


      } catch (error) {

        console.error(
          "Comparison error:",
          error
        );


        setComparisonError(
          error.message
        );


      } finally {

        setComparing(
          false
        );

      }

    };


  // =========================================================
  // GEMINI ANALYSIS
  // =========================================================

  const runAIAnalysis =
    async () => {

      if (!comparison) {

        setAiError(
          "Run a GPU comparison first."
        );

        return;

      }


      setAiLoading(
        true
      );

      setAiError(
        null
      );

      setAiAnalysis(
        null
      );


      try {

        const response =
          await fetch(
            `${API_URL}/api/benchmark/ai-analysis`,
            {

              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({
                  comparison:
                    comparison,
                }),

            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            data.detail ||
            "Gemini analysis failed."
          );

        }


        if (!data.success) {

          throw new Error(
            "Gemini analysis failed."
          );

        }


        setAiAnalysis(
          data.analysis
        );


      } catch (error) {

        console.error(
          "Gemini error:",
          error
        );


        setAiError(
          error.message
        );


      } finally {

        setAiLoading(
          false
        );

      }

    };


  // =========================================================
  // SELECTED SESSIONS
  // =========================================================

  const selectedSessionA =
    sessions.find(
      session =>
        session.session_id ===
        sessionA
    );


  const selectedSessionB =
    sessions.find(
      session =>
        session.session_id ===
        sessionB
    );


  // =========================================================
  // COMPARISON CHART
  // =========================================================

  const comparisonChartData =
    useMemo(() => {

      if (!comparison) {
        return [];
      }


      return (
        comparison.comparisons || []
      ).map(
        item => ({

          matrix:
            `${item.matrix_size}²`,

          gpuA:
            Number(
              item.gpu_a_gflops
            ),

          gpuB:
            Number(
              item.gpu_b_gflops
            ),

        })
      );

    }, [comparison]);


  // =========================================================
  // AI SECTION
  // =========================================================

  const renderAIAnalysis =
    () => {

      if (!aiAnalysis) {
        return null;
      }


      /*
       * This supports the new JSON response.
       *
       * It also has a fallback for an older string
       * response, so the UI won't crash if an old
       * backend response is still cached.
       */

      if (
        typeof aiAnalysis ===
        "string"
      ) {

        return (

          <div
            style={{
              color: "#c9d1d9",
              lineHeight: 1.7,
              whiteSpace: "pre-wrap",
            }}
          >
            {aiAnalysis
              .replace(
                /#{1,6}\s*/g,
                ""
              )
              .replace(
                /\*\*/g,
                ""
              )}

          </div>

        );

      }


      const findings =
        Array.isArray(
          aiAnalysis.key_findings
        )
          ? aiAnalysis.key_findings
          : [];


      return (

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0",
          }}
        >

          {/* ================================================= */}
          {/* OVERVIEW */}
          {/* ================================================= */}

          <div
            style={{
              padding:
                "20px 0",
              borderBottom:
                "1px solid #252b36",
            }}
          >

            <div
              style={{
                color:
                  "#35d49a",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "10px",
              }}
            >
              OVERVIEW
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "#c9d1d9",
                fontSize:
                  "14px",
                lineHeight:
                  "1.7",
              }}
            >
              {aiAnalysis.overview}
            </p>

          </div>


          {/* ================================================= */}
          {/* KEY FINDINGS */}
          {/* ================================================= */}

          <div
            style={{
              padding:
                "20px 0",
              borderBottom:
                "1px solid #252b36",
            }}
          >

            <div
              style={{
                color:
                  "#35d49a",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "12px",
              }}
            >
              KEY FINDINGS
            </div>


            <div
              style={{
                display:
                  "flex",
                flexDirection:
                  "column",
                gap:
                  "10px",
              }}
            >

              {findings.map(
                (
                  finding,
                  index
                ) => (

                  <div
                    key={
                      index
                    }
                    style={{
                      display:
                        "flex",
                      gap:
                        "12px",
                      color:
                        "#c9d1d9",
                      fontSize:
                        "14px",
                      lineHeight:
                        "1.6",
                    }}
                  >

                    <span
                      style={{
                        color:
                          "#35d49a",
                        fontWeight:
                          "800",
                        flexShrink:
                          0,
                      }}
                    >
                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}
                    </span>


                    <span>
                      {finding}
                    </span>

                  </div>

                )
              )}

            </div>

          </div>


          {/* ================================================= */}
          {/* SCALING */}
          {/* ================================================= */}

          <div
            style={{
              padding:
                "20px 0",
              borderBottom:
                "1px solid #252b36",
            }}
          >

            <div
              style={{
                color:
                  "#35d49a",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "10px",
              }}
            >
              SCALING ANALYSIS
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "#c9d1d9",
                fontSize:
                  "14px",
                lineHeight:
                  "1.7",
              }}
            >
              {
                aiAnalysis.scaling_analysis
              }
            </p>

          </div>


          {/* ================================================= */}
          {/* STABILITY */}
          {/* ================================================= */}

          <div
            style={{
              padding:
                "20px 0",
              borderBottom:
                "1px solid #252b36",
            }}
          >

            <div
              style={{
                color:
                  "#35d49a",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "10px",
              }}
            >
              STABILITY ANALYSIS
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "#c9d1d9",
                fontSize:
                  "14px",
                lineHeight:
                  "1.7",
              }}
            >
              {
                aiAnalysis.stability_analysis
              }
            </p>

          </div>


          {/* ================================================= */}
          {/* PERFORMANCE */}
          {/* ================================================= */}

          <div
            style={{
              padding:
                "20px 0",
              borderBottom:
                "1px solid #252b36",
            }}
          >

            <div
              style={{
                color:
                  "#35d49a",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "10px",
              }}
            >
              PERFORMANCE INTERPRETATION
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "#c9d1d9",
                fontSize:
                  "14px",
                lineHeight:
                  "1.7",
              }}
            >
              {
                aiAnalysis.performance_interpretation
              }
            </p>

          </div>


          {/* ================================================= */}
          {/* RECOMMENDATION */}
          {/* ================================================= */}

          <div
            style={{
              marginTop:
                "20px",
              padding:
                "20px",
              border:
                "1px solid #35d49a",
              borderRadius:
                "10px",
              background:
                "rgba(53, 212, 154, 0.06)",
            }}
          >

            <div
              style={{
                color:
                  "#35d49a",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "10px",
              }}
            >
              RECOMMENDATION
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "#f0f6fc",
                fontSize:
                  "15px",
                lineHeight:
                  "1.7",
              }}
            >
              {
                aiAnalysis.recommendation
              }
            </p>

          </div>


          {/* ================================================= */}
          {/* CAVEAT */}
          {/* ================================================= */}

          <div
            style={{
              marginTop:
                "16px",
              padding:
                "16px",
              borderRadius:
                "10px",
              background:
                "#151a21",
            }}
          >

            <div
              style={{
                color:
                  "#8b949e",
                fontSize:
                  "11px",
                fontWeight:
                  "800",
                letterSpacing:
                  "0.1em",
                marginBottom:
                  "8px",
              }}
            >
              IMPORTANT CAVEAT
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "#8b949e",
                fontSize:
                  "13px",
                lineHeight:
                  "1.6",
              }}
            >
              {aiAnalysis.caveat}
            </p>

          </div>

        </div>

      );

    };


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="app">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <header className="header">

        <div>

          <h1>
            ComputeBench
          </h1>

          <p>
            GPU Performance Laboratory
          </p>

        </div>


        <div className="status">

          <span className="status-dot"></span>

          CUDA LAB

        </div>

      </header>


      <main className="container">

        {/* ================================================== */}
        {/* ERROR */}
        {/* ================================================== */}

        {error && (

          <div className="error">

            <strong>
              Error:
            </strong>

            {" "}

            {error}

          </div>

        )}


        {/* ================================================== */}
        {/* GPU */}
        {/* ================================================== */}

        <section className="gpu-card">

          <div>

            <span className="label">
              GPU
            </span>


            <h2>

              {gpu?.name ||
                "Detecting GPU..."}

            </h2>

          </div>


          <div className="gpu-status">

            <span className="status-dot"></span>

            {gpu?.available
              ? "CUDA AVAILABLE"
              : "CUDA UNAVAILABLE"}

          </div>

        </section>


        {/* ================================================== */}
        {/* STATS */}
        {/* ================================================== */}

        <section className="stats-grid">

          <div className="stat-card">

            <span className="label">
              CUDA VERSION
            </span>

            <strong>

              {gpu?.cuda_version ||
                "--"}

            </strong>

          </div>


          <div className="stat-card">

            <span className="label">
              VRAM
            </span>

            <strong>

              {gpu?.vram_gb
                ? `${gpu.vram_gb} GB`
                : "--"}

            </strong>

          </div>


          <div className="stat-card">

            <span className="label">
              WORKLOAD
            </span>

            <strong>
              Matrix Multiply
            </strong>

          </div>

        </section>


        {/* ================================================== */}
        {/* TELEMETRY */}
        {/* ================================================== */}

        <section className="telemetry-section">

          <div className="section-title">

            <div>

              <span className="label">
                LIVE MONITORING
              </span>

              <h2>
                GPU Telemetry
              </h2>

            </div>


            <div className="live-indicator">

              <span className="status-dot"></span>

              LIVE

            </div>

          </div>


          <div className="telemetry-grid">

            <div className="telemetry-card">

              <div className="telemetry-header">

                <span>
                  GPU UTILIZATION
                </span>

                <strong>

                  {telemetry
                    ? `${telemetry.gpu_utilization_percent}%`
                    : "--"}

                </strong>

              </div>


              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{
                    width: `${
                      telemetry
                        ? telemetry.gpu_utilization_percent
                        : 0
                    }%`,
                  }}
                />

              </div>

            </div>


            <div className="telemetry-card">

              <div className="telemetry-header">

                <span>
                  VRAM USAGE
                </span>

                <strong>

                  {telemetry
                    ? `${formatNumber(
                        telemetry.vram_used_mb,
                        0
                      )} MB`
                    : "--"}

                </strong>

              </div>

            </div>


            <div className="telemetry-card metric">

              <span>
                TEMPERATURE
              </span>

              <strong>

                {telemetry
                  ? `${telemetry.temperature_c}°C`
                  : "--"}

              </strong>

            </div>


            <div className="telemetry-card metric">

              <span>
                POWER
              </span>

              <strong>

                {telemetry?.power_w !==
                  null &&
                telemetry?.power_w !==
                  undefined
                  ? `${telemetry.power_w} W`
                  : "--"}

              </strong>

            </div>

          </div>

        </section>


        {/* ================================================== */}
        {/* BENCHMARK */}
        {/* ================================================== */}

        <section className="benchmark-card">

          <div className="section-heading">

            <div>

              <span className="label">
                GPU BENCHMARK
              </span>

              <h2>
                Matrix Multiplication
              </h2>

              <p>
                Measures floating-point
                computation performance
                across different matrix sizes.
              </p>

            </div>


            <button
              className="benchmark-button"
              onClick={
                runBenchmark
              }
              disabled={
                runningBenchmark
              }
            >

              {runningBenchmark
                ? "RUNNING..."
                : "RUN BENCHMARK"}

            </button>

          </div>


          {runningBenchmark && (

            <div className="running">

              <div className="loader"></div>

              <span>
                Running CUDA benchmark...
              </span>

            </div>

          )}


          {/* ================================================= */}
          {/* RESULTS */}
          {/* ================================================= */}

          {results.length > 0 && (

            <>

              {summary && (

                <div className="summary-grid">

                  <div className="summary-card">

                    <span>
                      AVERAGE GFLOPS
                    </span>

                    <strong>
                      {formatNumber(
                        summary.averageGflops
                      )}
                    </strong>

                  </div>


                  <div className="summary-card">

                    <span>
                      PEAK GFLOPS
                    </span>

                    <strong>
                      {formatNumber(
                        summary.peakGflops
                      )}
                    </strong>

                  </div>


                  <div className="summary-card">

                    <span>
                      FASTEST MATRIX
                    </span>

                    <strong>
                      {summary.fastestMatrix}²
                    </strong>

                  </div>


                  <div className="summary-card">

                    <span>
                      TOTAL RUNS
                    </span>

                    <strong>
                      {summary.totalRuns}
                    </strong>

                  </div>

                </div>

              )}


              <div className="detailed-results">

                <div className="section-title">

                  <div>

                    <span className="label">
                      DETAILED RESULTS
                    </span>

                    <h3>
                      Matrix Benchmark
                    </h3>

                  </div>

                </div>


                <div className="results-table">

                  <div className="table-row table-header">

                    <span>
                      Matrix Size
                    </span>

                    <span>
                      Average
                    </span>

                    <span>
                      Median
                    </span>

                    <span>
                      GFLOPS
                    </span>

                    <span>
                      Std Dev
                    </span>

                    <span>
                      VRAM
                    </span>

                  </div>


                  {results.map(
                    result => (

                      <div
                        className="table-row"
                        key={
                          result.matrix_size
                        }
                      >

                        <span>

                          {result.matrix_size}
                          {" × "}
                          {result.matrix_size}

                        </span>


                        <span>

                          {formatNumber(
                            result.mean_ms,
                            3
                          )}
                          {" ms"}

                        </span>


                        <span>

                          {formatNumber(
                            result.median_ms,
                            3
                          )}
                          {" ms"}

                        </span>


                        <span className="performance">

                          {formatNumber(
                            result.gflops
                          )}

                        </span>


                        <span>

                          ±{" "}
                          {formatNumber(
                            result.std_dev_ms,
                            3
                          )}
                          {" ms"}

                        </span>


                        <span>

                          {formatNumber(
                            result.gpu_memory_mb,
                            2
                          )}
                          {" MB"}

                        </span>

                      </div>

                    )
                  )}

                </div>

              </div>


              <div className="chart-container">

                <h3>
                  Performance Scaling
                </h3>


                <ResponsiveContainer
                  width="100%"
                  height={350}
                >

                  <LineChart
                    data={results}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="matrix_size"
                      tickFormatter={
                        value =>
                          `${value}²`
                      }
                    />

                    <YAxis />

                    <Tooltip />

                    <Line
                      type="monotone"
                      dataKey="gflops"
                      strokeWidth={3}
                      dot={{ r: 5 }}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            </>

          )}

        </section>


        {/* ================================================== */}
        {/* GPU COMPARISON */}
        {/* ================================================== */}

        <section className="comparison-section">

          <div className="comparison-header">

            <span className="label">
              GPU COMPARISON
            </span>

            <h2>
              GPU vs GPU
            </h2>

            <p>
              Compare two benchmark sessions
              using the same workloads.
            </p>

          </div>


          <div className="comparison-selectors">

            {/* GPU A */}

            <div className="comparison-selector">

              <span className="label">
                GPU A
              </span>


              <select
                value={sessionA}
                onChange={
                  event => {

                    setSessionA(
                      event.target.value
                    );

                    setComparison(
                      null
                    );

                    setAiAnalysis(
                      null
                    );

                  }
                }
              >

                <option value="">
                  Select first GPU
                </option>


                {sessions.map(
                  session => (

                    <option
                      key={
                        session.session_id
                      }
                      value={
                        session.session_id
                      }
                    >

                      {session.gpu_name}
                      {" • "}
                      {session.session_id}

                    </option>

                  )
                )}

              </select>


              {selectedSessionA && (

                <div className="selected-gpu-info">

                  <strong>
                    {selectedSessionA.gpu_name}
                  </strong>

                  <span>
                    {selectedSessionA.session_id}
                  </span>

                </div>

              )}

            </div>


            <div className="comparison-vs">
              VS
            </div>


            {/* GPU B */}

            <div className="comparison-selector">

              <span className="label">
                GPU B
              </span>


              <select
                value={sessionB}
                onChange={
                  event => {

                    setSessionB(
                      event.target.value
                    );

                    setComparison(
                      null
                    );

                    setAiAnalysis(
                      null
                    );

                  }
                }
              >

                <option value="">
                  Select second GPU
                </option>


                {sessions.map(
                  session => (

                    <option
                      key={
                        session.session_id
                      }
                      value={
                        session.session_id
                      }
                    >

                      {session.gpu_name}
                      {" • "}
                      {session.session_id}

                    </option>

                  )
                )}

              </select>


              {selectedSessionB && (

                <div className="selected-gpu-info">

                  <strong>
                    {selectedSessionB.gpu_name}
                  </strong>

                  <span>
                    {selectedSessionB.session_id}
                  </span>

                </div>

              )}

            </div>

          </div>


          <div className="comparison-action">

            <button
              className="benchmark-button"
              onClick={
                runComparison
              }
              disabled={
                comparing ||
                !sessionA ||
                !sessionB
              }
            >

              {comparing
                ? "COMPARING..."
                : "COMPARE GPUs"}

            </button>

          </div>


          {comparisonError && (

            <div className="error">

              <strong>
                Comparison Error:
              </strong>

              {" "}

              {comparisonError}

            </div>

          )}


          {/* ================================================= */}
          {/* COMPARISON */}
          {/* ================================================= */}

          {comparison && (

            <div className="comparison-results">

              <div className="comparison-winner">

                <span className="label">
                  OVERALL WINNER
                </span>


                <h2>

                  {comparison.summary
                    ?.overall_winner ===
                  "A"

                    ? comparison.gpu_a.name

                    : comparison.summary
                        ?.overall_winner ===
                      "B"

                    ? comparison.gpu_b.name

                    : "TIE"}

                </h2>


                {comparison.summary
                  ?.overall_winner !==
                  "TIE" && (

                  <p>

                    {formatNumber(
                      comparison.summary
                        ?.overall_difference_percent
                    )}

                    %

                    {" faster on average"}

                  </p>

                )}

              </div>


              {/* GPU CARDS */}

              <div className="comparison-gpu-grid">

                <div className="comparison-gpu-card">

                  <span className="label">
                    GPU A
                  </span>

                  <h3>
                    {comparison.gpu_a.name}
                  </h3>

                  <strong>

                    {formatNumber(
                      comparison.summary
                        ?.gpu_a_average_gflops
                    )}

                    {" GFLOPS"}

                  </strong>

                </div>


                <div className="comparison-gpu-card">

                  <span className="label">
                    GPU B
                  </span>

                  <h3>
                    {comparison.gpu_b.name}
                  </h3>

                  <strong>

                    {formatNumber(
                      comparison.summary
                        ?.gpu_b_average_gflops
                    )}

                    {" GFLOPS"}

                  </strong>

                </div>

              </div>


              {/* COMPARISON TABLE */}

              <div className="comparison-table-container">

                <div className="section-title">

                  <div>

                    <span className="label">
                      DETAILED COMPARISON
                    </span>

                    <h3>
                      Workload Results
                    </h3>

                  </div>

                </div>


                <div className="comparison-table">

                  <div className="comparison-table-row comparison-table-header">

                    <span>
                      Matrix
                    </span>

                    <span>
                      {comparison.gpu_a.name}
                    </span>

                    <span>
                      {comparison.gpu_b.name}
                    </span>

                    <span>
                      Difference
                    </span>

                    <span>
                      Winner
                    </span>

                  </div>


                  {(
                    comparison.comparisons ||
                    []
                  ).map(
                    item => (

                      <div
                        className="comparison-table-row"
                        key={
                          item.matrix_size
                        }
                      >

                        <span>
                          {item.matrix_size}²
                        </span>


                        <span>

                          {formatNumber(
                            item.gpu_a_gflops
                          )}
                          {" GFLOPS"}

                        </span>


                        <span>

                          {formatNumber(
                            item.gpu_b_gflops
                          )}
                          {" GFLOPS"}

                        </span>


                        <span>

                          {item.percentage_difference >=
                          0
                            ? "+"
                            : ""}

                          {formatNumber(
                            item.percentage_difference
                          )}
                          %

                        </span>


                        <span className="comparison-winner-cell">

                          {item.winner ===
                          "A"

                            ? comparison.gpu_a.name

                            : item.winner ===
                              "B"

                            ? comparison.gpu_b.name

                            : "TIE"}

                        </span>

                      </div>

                    )
                  )}

                </div>

              </div>


              {/* COMPARISON GRAPH */}

              <div className="comparison-chart">

                <div className="section-title">

                  <span className="label">
                    PERFORMANCE SCALING
                  </span>

                  <h3>
                    GPU vs GPU
                  </h3>

                </div>


                <ResponsiveContainer
                  width="100%"
                  height={380}
                >

                  <LineChart
                    data={
                      comparisonChartData
                    }
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="matrix"
                    />

                    <YAxis />

                    <Tooltip />

                    <Legend />


                    <Line
                      type="monotone"
                      dataKey="gpuA"
                      name={
                        comparison.gpu_a.name
                      }
                      strokeWidth={3}
                      dot={{ r: 5 }}
                    />


                    <Line
                      type="monotone"
                      dataKey="gpuB"
                      name={
                        comparison.gpu_b.name
                      }
                      strokeWidth={3}
                      dot={{ r: 5 }}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>


              {/* ================================================= */}
              {/* GEMINI AI */}
              {/* ================================================= */}

              <div
                className="ai-analysis-placeholder"
              >

                <div
                  style={{
                    display:
                      "flex",
                    alignItems:
                      "center",
                    justifyContent:
                      "space-between",
                    gap:
                      "16px",
                  }}
                >

                  <div>

                    <span className="label">
                      AI PERFORMANCE ANALYSIS
                    </span>

                    <h3>
                      Gemini Performance Analyst
                    </h3>

                  </div>


                  <span
                    style={{
                      border:
                        "1px solid #35d49a",
                      color:
                        "#35d49a",
                      borderRadius:
                        "20px",
                      padding:
                        "6px 12px",
                      fontSize:
                        "11px",
                      fontWeight:
                        "800",
                      letterSpacing:
                        "0.05em",
                      flexShrink:
                        0,
                    }}
                  >
                    GEMINI
                  </span>

                </div>


                <p>
                  AI-powered interpretation of
                  your measured GPU performance,
                  scaling and stability.
                </p>


                <button
                  className="benchmark-button"
                  onClick={
                    runAIAnalysis
                  }
                  disabled={
                    aiLoading
                  }
                >

                  {aiLoading
                    ? "ANALYZING..."
                    : "ASK GEMINI TO ANALYZE"}

                </button>


                {aiError && (

                  <div className="error">

                    <strong>
                      Gemini Error:
                    </strong>

                    {" "}

                    {aiError}

                  </div>

                )}


                {aiAnalysis && (

                  <div
                    style={{
                      marginTop:
                        "24px",
                      borderTop:
                        "1px solid #252b36",
                      paddingTop:
                        "8px",
                    }}
                  >

                    {renderAIAnalysis()}

                  </div>

                )}

              </div>

            </div>

          )}


          {!comparison &&
            !comparing && (

            <div className="comparison-empty">

              <div className="empty-icon">
                VS
              </div>

              <h3>
                Compare two GPUs
              </h3>

              <p>
                Select two benchmark sessions
                above to compare their performance.
              </p>

            </div>

          )}

        </section>


        {/* ================================================== */}
        {/* HISTORY */}
        {/* ================================================== */}

        <section className="history-section">

          <div className="history-header">

            <div>

              <span className="label">
                PERFORMANCE HISTORY
              </span>

              <h2>
                Benchmark History
              </h2>

            </div>

          </div>


          {loadingHistory ? (

            <div className="history-empty">
              Loading history...
            </div>

          ) : historySessions.length ===
            0 ? (

            <div className="history-empty">

              <div className="empty-icon">
                LOG
              </div>

              <h3>
                No benchmark history
              </h3>

              <p>
                Run your first benchmark to
                start building performance history.
              </p>

            </div>

          ) : (

            <div className="history-table">

              <div className="history-row history-table-header">

                <span>
                  SESSION
                </span>

                <span>
                  DATE
                </span>

                <span>
                  GPU
                </span>

                <span>
                  4096² GFLOPS
                </span>

              </div>


              {historySessions.map(
                session => {

                  const result4096 =
                    session.results.find(
                      result =>
                        Number(
                          result.matrix_size
                        ) === 4096
                    );


                  return (

                    <div
                      className="history-row"
                      key={
                        session.session_id
                      }
                    >

                      <span>
                        {session.session_id}
                      </span>

                      <span>
                        {formatDate(
                          session.timestamp
                        )}
                      </span>

                      <span>
                        {session.gpu_name}
                      </span>

                      <span className="performance">

                        {result4096
                          ? formatNumber(
                              result4096.gflops
                            )
                          : "--"}

                      </span>

                    </div>

                  );

                }
              )}

            </div>

          )}

        </section>

      </main>

    </div>

  );

}


export default App;