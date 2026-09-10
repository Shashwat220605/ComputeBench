# Contributing to ComputeBench

ComputeBench is a benchmark-oriented project, so reproducibility and clear measurements matter as much as code changes.

## Workflow

1. Branch from `main` using a focused branch name.
2. Make one logical change per pull request.
3. Run the relevant benchmark or test suite before opening the pull request.
4. Record important environment details when performance numbers change.
5. Explain methodology and validation in the pull request description.

## Benchmarking guidelines

- Keep benchmark inputs consistent when comparing revisions.
- Report enough context to reproduce a measurement.
- Avoid presenting a single noisy run as a definitive performance result.
- Separate correctness regressions from expected performance trade-offs.

## Pull requests

Use descriptive titles and include the commands used for validation. For performance changes, summarize the before/after behavior and note any hardware or runtime assumptions.