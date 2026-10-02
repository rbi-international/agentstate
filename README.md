# AgentState

AgentState investigates whether a learned execution-state representation of
partial LLM-agent trajectories transfers across models and frameworks while
retaining useful execution signals and reducing source-identity leakage.

**Status:** candidate research direction. Novelty and effectiveness are not
established. The authoritative research protocol is
[docs/EXPERIMENT_BASE.md](docs/EXPERIMENT_BASE.md). Its schemas are conceptual
and labeling strategies are proposed; neither is validated or operationally finalized.

The current stage is **project foundation**, followed by protocol
operationalization and two-trace validation. Schemas, manifest requirements,
label definitions, and validation criteria need operationalization before runs.

## Pilot and first experiment

The pilot models are **Qwen3-4B-Instruct-2507** and **Llama-3.2-3B-Instruct**;
the pilot frameworks are **AutoGen** and **LangGraph**. Exact model revisions
and experiment settings must be recorded before execution.

The first experiment will run one SWE-bench task with Qwen + AutoGen, manually
inspect the raw trace, then run the same task with Qwen + LangGraph. Both traces
must be normalized and checked for comparable, preserved evidence before scaling.
This experiment has not been run.

## Current repository layout

```text
AgentState/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── .gitignore
├── agentstate/
│   ├── __init__.py
│   ├── adapters/{autogen,langgraph}/
│   ├── baselines/
│   ├── collectors/
│   ├── evaluation/
│   ├── labeling/
│   ├── models/
│   ├── normalization/
│   ├── probes/
│   ├── representation/
│   ├── retrieval/
│   ├── schemas/
│   └── validation/
├── configs/{experiments,frameworks,models,tasks}/
├── docs/EXPERIMENT_BASE.md
├── experiments/
│   ├── stage01_trace_validation/
│   ├── stage02_micro_pilot/
│   └── stage03_mini_pilot/
├── tests/
├── data/                     # ignored local artifacts
└── reports/                  # ignored local reports
```

Implemented foundation: packaging/dependency configuration, Git ignore rules,
research protocol, project instructions, minimal package initializer, and directory
placeholders. Component directories currently contain placeholders only.
Validated schemas, labeling logic, providers, collectors, adapters, normalization,
baselines, encoders, training, probes, retrieval, and evaluation remain planned.
There are no tests or experimental results yet.

Generated installation metadata (`*.egg-info/`), data, reports, weights, and
checkpoints are ignored by Git. Generated artifacts require separate storage;
artifact storage and archival infrastructure have not been implemented.

## Existing environment

From the repository root, activate the existing Conda environment and install
the project in editable mode with development dependencies:

```sh
conda activate agentstate
python -m pip install -e ".[dev]"
```

Expected interpreter: `C:\Users\rbhar\anaconda3\envs\agentstate\python.exe`
(Python 3.11.17). Check `python -c "import sys; print(sys.executable)"` before
using it. The editable installation already exists; the command above documents
setup rather than indicating another installation is needed.

```sh
python -m pip check
python -c "import agentstate; print(agentstate.__file__)"
```

Use the `agentstate` environment, keep dependencies minimal, and record exact
versions in future experiment manifests. Follow the protocol's stage gates;
the current foundation does not establish a frozen schema or completed Stage 0.
