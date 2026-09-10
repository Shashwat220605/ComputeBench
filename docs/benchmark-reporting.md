# Benchmark reporting

Performance results are easier to trust when the measurement context is explicit.

## Recommended report

Include:

- benchmark name and version
- input size or workload
- hardware and operating system
- compiler/runtime version when relevant
- number of repetitions or warm-up strategy
- representative result and units
- comparison baseline

Avoid comparing results collected under materially different workloads without explaining the difference. If variance is significant, report it rather than selecting only the fastest run.