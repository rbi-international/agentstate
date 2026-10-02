# AgentState v0.1 — Experimental Base

**Working title:** *AgentState: Learning Framework- and Model-Invariant Execution Representations for LLM Agents*
**Status:** Source of truth for the pilot
**Version:** 0.1 — 2026-10-02

## Core Research Question

> Can a single learned encoder map heterogeneous partial LLM-agent trajectories into a useful execution-state representation that generalizes across models and frameworks while reducing source-specific leakage?

The target representation is: `E_theta(trajectory_1:t) -> z_t in R^d`.

AgentState is **not** initially another coding agent, orchestration framework, router, verifier, or recovery controller. Its scientific target is representation and out-of-distribution generalization.

## Novelty Boundary

We will not claim novelty for framework-independent specifications, cross-model trajectory analysis, failure prediction, rollback/restart, model routing, behavioral taxonomies, observability, task-specific decision landscapes, or generic trajectory value models.

Candidate gap: a **single learned execution-state encoder** that consumes normalized partial trajectories without rebuilding a task-specific graph/taxonomy, and whose **frozen representation transfers across unseen model/framework combinations and multiple downstream tasks**.

Closest threats to track explicitly: TraceGraph, Open Agent Specification, AutoTraceGT, plus adjacent failure/recovery/value-model literature.

## Hypotheses

- **H1:** A held-out model-framework combination retains useful execution-state signal.
- **H2:** AgentState exposes less model/framework identity than surface-text embeddings while retaining task utility.
- **H3:** One frozen encoder supports several small downstream heads.
- **H4:** Cross-framework/model retrieval reflects execution semantics rather than wording/tool-name similarity.
- **H5:** AgentState loses less performance under OOD shift than generic embeddings.

## Execution State Definition

At step `t`, state is derived from the observable trajectory prefix, environment evidence, and resource state.

**Semantic channel:** strategy/hypothesis, intended action, behavioral pattern, expressed uncertainty, recovery attempts, relevant observations.

**Execution channel:** tools/outcomes, tests, errors, files inspected/modified, environment deltas, repeated actions, tokens, tool calls, elapsed time.

Ablations must compare semantic-only, execution-only, and fused representations.

## Mini-Pilot Configuration

**Models:** Qwen3-4B-Instruct-2507 and Llama-3.2-3B-Instruct. Exact revisions, inference engine, quantization, context settings, and licenses must be frozen in an experiment manifest.

**Frameworks:** AutoGen and LangGraph. CrewAI is reserved as a later unseen-framework test.

**Tasks:** approximately 50 stratified SWE-bench Lite tasks. Selection must be scripted and version-controlled; never simply take the first 50.

| Model | AutoGen | LangGraph |
|---|---|---|
| Qwen3-4B | QA | QL |
| Llama-3.2-3B | LA | LL |

One run over 50 tasks = **200 trajectories**. Three runs = 600. **Do not begin with 600.**

## Mandatory First Experiment

1. Run **one SWE-bench task with Qwen3-4B + AutoGen**.
2. Manually verify that the trace records intent/action, tool invocation, observation, environment change, objective improvement/regression, resource use, and enough evidence for reconstruction.
3. Run the **same task with Qwen3-4B + LangGraph**.
4. Normalize both traces.
5. Do not scale until the normalized traces are comparable without unnecessary framework syntax.

## Canonical Event Schema

```json
{
  "schema_version": "0.1",
  "trajectory_id": "string",
  "task_id": "string",
  "step_id": 0,
  "source": {
    "model_id": "string",
    "model_revision": "string",
    "framework_id": "string",
    "framework_version": "string",
    "run_id": "string",
    "seed": 0
  },
  "event": {
    "event_type": "reasoning|action|tool_call|observation|environment_change|final",
    "semantic_content": "string|null",
    "tool_family": "string|null",
    "tool_name": "string|null",
    "execution_status": "success|failure|partial|unknown"
  },
  "environment": {
    "files_inspected": [],
    "files_modified": [],
    "tests_passed": null,
    "tests_failed": null,
    "new_failures": null,
    "resolved_failures": null,
    "error_signatures": [],
    "patch_summary": null
  },
  "resources": {
    "input_tokens": null,
    "output_tokens": null,
    "cumulative_tokens": null,
    "tool_calls": null,
    "elapsed_ms": null
  },
  "outcome": {
    "terminal": false,
    "final_success": null
  }
}
```

Schema changes require a version bump and migration note. Hidden chain-of-thought is neither assumed nor required.

## State Snapshot Schema

```json
{
  "state_id": "string",
  "trajectory_id": "string",
  "task_id": "string",
  "step": 0,
  "trajectory_prefix_ref": "string",
  "semantic_state": {"recent_events": [], "agent_summary": null},
  "execution_state": {
    "files_inspected_count": 0,
    "files_modified_count": 0,
    "tests_passed": null,
    "tests_failed": null,
    "test_delta": null,
    "tool_successes": 0,
    "tool_failures": 0,
    "repeated_action_score": null,
    "active_error_signatures": []
  },
  "resource_state": {
    "cumulative_input_tokens": null,
    "cumulative_output_tokens": null,
    "cumulative_tool_calls": 0,
    "elapsed_ms": null
  },
  "future_outcome": {
    "eventual_success": null,
    "steps_to_terminal": null,
    "tokens_to_terminal": null,
    "future_recovery_observed": null
  }
}
```

**Future-outcome fields are labels only and must never enter encoder input.**

## Objective Signals and Labels

Prefer environment-derived evidence: passing/failing tests, new/resolved failures, tool success/failure, compiler/runtime errors, repeated actions, file-touch patterns, patch size, rollback/reversion, steps since measurable improvement, and resource use.

Candidate behavioral labels: `exploring`, `progressing`, `stagnant`, `regressing`, `recovering`, `recovered`, `looping`, `terminal_success`, `terminal_failure`, `unknown`.

Every derived label requires an operational definition, ambiguity rule, version, and—where manual—a reliability check.

## Ground Truth Hierarchy

1. **Deterministic evidence:** tests, tool results, errors, repository changes, terminal outcome.
2. **Derived structural evidence:** repeated failures, sustained improvement, recovery after regression.
3. **Human annotation:** limited semantic-equivalence/behavior subset with agreement measurement.
4. **LLM-assisted annotation:** assistance only; never silently treated as unquestionable ground truth.

## Pair Construction

**Positive pairs:** equivalent execution conditions across different models/frameworks/repositories.

**Negatives:** meaningfully different states, such as productive localization versus uncontrolled regression.

**Hard negatives:** similar surface text/tools but opposite semantics; e.g., `pytest` failures decreasing 14→3 versus increasing 3→14.

## Candidate Learning Objective

Start with a multi-objective design combining contrastive, progress, outcome, behavior, and invariance losses. The exact invariance mechanism is not frozen: adversarial learning, gradient reversal, regularization, or other approaches must be compared.

## Leakage Prevention

- **Future leakage:** no future events, final outcome, future tests, steps-to-terminal, or later recovery information in state input.
- **Framework leakage:** normalize/remove native class names, serialization markers, internal node IDs, and boilerplate unless semantically necessary.
- **Model leakage:** retain model ID as metadata, not encoder input during invariance experiments.
- **Task/repository leakage:** use task- and repository-aware analysis; avoid near-duplicate artifacts across splits.
- **Annotation leakage:** labels derived using final outcome must be marked and never fed back as predictor features.

## Baselines Before a Large Encoder

- **B0:** structured execution features only.
- **B1:** generic text embedding of normalized trajectory prefix.
- **B2:** trajectory-summary embedding.
- **B3:** semantic embedding + structured features.
- **B4:** reproducible TraceGraph-/AutoTraceGT-inspired features where applicable.

If simple baselines match AgentState on OOD transfer, a large specialized encoder is not justified.

## Evaluation Splits

- **A — IID sanity check:** never the main claim.
- **B — Held-out model-framework pair:** e.g. train QA + QL + LA, test LL.
- **C — Unseen model:** later hold out an entire model family.
- **D — Unseen framework:** train AutoGen + LangGraph; later test CrewAI.
- **E — Unseen domain:** later train coding/web and test scientific/data agents.
- **F — Compositional OOD:** unseen model + unseen framework + unseen domain.

The strongest claims must be based on OOD splits.

## Frozen-Encoder Probes

Freeze the encoder and train small heads for failure risk, progress, remaining steps/cost, recoverability, behavioral class, and later intervention utility.

## Cross-Framework Retrieval

Given a query state from one model/framework, retrieve nearest states from a different model/framework. Evaluate semantic relevance rather than wording similarity. Candidate metrics: Recall@K, MRR, NDCG, plus human pairwise relevance agreement.

## Invariance Evaluation

Train probes from `z` to `framework_id` and `model_id`. Desired behavior is a **utility–leakage trade-off**: high execution-state utility with lower source-identity predictability than competing representations.

Do not claim statistical independence unless explicitly defined and measured.

## Ablations

Compare full AgentState against variants without semantic channel, execution channel, invariance objective, contrastive objective, behavioral supervision, and with different trajectory windows/normalization strengths.

## Falsification / Kill Criteria

Reconsider or kill AgentState if:

1. it works IID but collapses on held-out model/framework conditions;
2. generic text embeddings perform essentially as well;
3. structured execution features alone explain nearly all useful signal;
4. framework/model identity dominates the embedding;
5. cross-framework semantic retrieval is weak;
6. one representation does not transfer between downstream tasks;
7. annotation reliability is too poor to establish semantic-state equivalence;
8. improvements disappear under repository/task-aware splits.

These criteria are defined **before** large-scale training.

## What Success Means

> Under held-out model/framework evaluation, AgentState retains more downstream execution-state utility than generic trajectory embeddings while leaking less source identity.

A stronger result is one frozen encoder supporting several downstream tasks and cross-framework retrieval without rebuilding task-specific graphs or taxonomies.

Exact numerical thresholds must be decided after pilot variance is known; they must not be invented to guarantee success.

## Reproducibility Requirements

Every run records Git commit, task ID, model/revision, framework/version, inference engine/version, prompt/template version, seed where controllable, sampling parameters, context limit, tool configuration, timeout/budget, hardware, timestamps, raw trace, normalized trace, evaluator version, and terminal outcome.

Raw traces remain immutable. Normalization creates derived artifacts.

## Proposed Repository Layout

```text
agentstate/
├── README.md
├── docs/
├── configs/
├── schemas/
├── adapters/autogen/
├── adapters/langgraph/
├── collectors/
├── environments/
├── tasks/
├── normalization/
├── labeling/
├── validation/
├── baselines/
├── representation/
├── probes/
├── retrieval/
├── evaluation/
├── experiments/
├── tests/
└── artifacts/{raw,normalized,reports}/
```

## Experiment Stages and Gates

**Stage 0 — Protocol freeze:** this document, schemas, manifest template.

**Stage 1 — Two-trace validation:** one task, Qwen×AutoGen and Qwen×LangGraph. Gate: normalization preserves critical evidence.

**Stage 2 — Micro-pilot:** ~5 tasks × 4 model/framework combinations. Gate: stable collection and extractable objective signals.

**Stage 3 — Mini-pilot:** ~50 tasks × 4 combinations. Gate: enough variation for baselines and held-out-pair evaluation.

**Stage 4 — Baseline study:** structured features vs generic embeddings vs summaries vs hybrid. Gate: evidence a specialized representation is warranted.

**Stage 5 — AgentState v0 encoder:** train the smallest reasonable representation model. Gate: OOD improvement plus acceptable source leakage.

**Stage 6 — Scale:** multiple seeds, additional model, CrewAI OOD test, broader tasks.

**Stage 7 — Full artifact:** encoder + dataset + benchmark + code + paper, only if results justify the claims.

## Immediate Next Task

1. Create the repository skeleton.
2. Convert the conceptual schemas into validated JSON Schema files.
3. Create an experiment manifest.
4. Implement the AutoGen raw-trace collector.
5. Run **one** SWE-bench task with Qwen3-4B + AutoGen.
6. Inspect it manually.
7. Implement the LangGraph collector for the same task.
8. Normalize both traces and produce a validation report.

Only then decide whether the schema is frozen enough for the 5-task micro-pilot.

## Research Discipline

- Never invent benchmark results.
- Never select only successful trajectories.
- Never hide failed runs.
- Never change the main evaluation split after seeing results without reporting it.
- Never use final outcomes as hidden input features.
- Never claim universality from two models and two frameworks; the pilot tests feasibility only.
- Never call a representation invariant solely from a t-SNE/UMAP plot.
- Report negative results and source-specific failure modes.
- Prefer a smaller falsifiable claim over a broad unsupported one.

## Current Decision

**AgentState v0.1 is a candidate research direction, not a confirmed novel contribution.**

The pilot exists to answer cheaply whether a reusable execution-state representation provides value beyond generic embeddings and simple structured features. If not, stop or reformulate before spending serious compute.
