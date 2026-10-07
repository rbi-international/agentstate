# AgentState data contracts

These are executable structural contracts for protocol v0.1, not empirical
validation of the conceptual schema or finalized scientific labeling rules.
[EXPERIMENT_BASE.md](EXPERIMENT_BASE.md) remains unchanged and authoritative.
All test records are explicitly synthetic; they provide software verification,
not experimental evidence. No agent execution, collection, normalization,
behavioral labeling, or training is implemented here.

## Implemented contracts and commands

`agentstate.schemas` exports Pydantic v2 `AgentEvent`, `StateSnapshot`, and
`ExperimentManifest`. Nested models use strict validation and reject extra
fields. All declared fields are required, including nullable fields: omission
is different from an explicit unknown value. Strings and booleans are not
coerced into integer counts. Nonfinite numbers are rejected.

From the repository root, use the existing environment:

```sh
conda activate agentstate
python -m agentstate.schemas.generate
python -m agentstate.schemas.validate manifest configs/experiments/qwen_autogen_trace_validation.yaml
python -m agentstate.schemas.validate manifest configs/experiments/qwen_autogen_trace_validation.yaml --run-ready
python -m agentstate.schemas.validate event PATH_TO_EVENT.json
python -m agentstate.schemas.validate snapshot PATH_TO_SNAPSHOT.json
python -m pytest -q tests/test_data_contracts.py --basetemp=.pytest_cache/contracts-tmp
python -m ruff check agentstate/schemas tests/test_data_contracts.py
python -m pip check
git diff --check
```

The draft passes structural validation and intentionally fails `--run-ready`
with exit code 1 and unresolved field paths. These commands never execute a run.
If activation does not select the environment, invoke
`C:\Users\rbhar\anaconda3\envs\agentstate\python.exe` explicitly (PowerShell
requires `&` before a quoted executable path).

Generation writes `agentstate/schemas/json/{AgentEvent,StateSnapshot,ExperimentManifest}.schema.json`.
Pydantic contracts are the sole definitions; do not hand-edit generated schemas.
The generator uses `Draft202012Validator.check_schema`. Tests regenerate into a
temporary directory, compare the checked-in output byte-for-byte, and validate
representative records with `jsonschema` and its format checker. JSON Schema
structural validation does not replace Python run-readiness checks or provenance
review; JSON numeric semantics also do not capture every strict Python type rule.

## Missing data and contract interpretations

- Event and snapshot names and nesting match the protocol. No event or snapshot
  field was added or renamed. Event `schema_version` is fixed to `0.1`; the
  protocol snapshot has no version field, so none is silently added.
- Protocol fields shown as null accept explicit `None`/JSON null/YAML null.
  Counts, tokens, step IDs, and millisecond durations are nonnegative integers.
  Unknown measurements never receive zero defaults. All fields have no defaults.
- Snapshot counts illustrated as zero (file counts, tool successes/failures,
  cumulative tool calls) are required non-null counts. Zero means an observed
  count of zero. If these cannot be observed, do not fabricate zero; representing
  unknown values there requires a proposed versioned protocol change.
- File lists and error-signature lists contain strings. An empty list means no
  entries recorded, not proof that collection was exhaustive. Unknown-versus-empty
  list semantics remain unresolved and are not solved by this contract.
- `semantic_state.recent_events` has an unspecified item shape in the conceptual
  example. This implementation provisionally uses the existing event-detail
  object (type, semantic content, tool family/name, execution status), rather than
  whole events, arbitrary dictionaries, or trajectory references. This narrows
  the unspecified list without changing field structure and needs pilot review.
- `test_delta` is a nullable signed integer with the observation definition below.
  It is not a behavioral label. No derivation is implemented.
- `repeated_action_score` is a nullable finite nonnegative number. No upper bound,
  formula, window, or looping threshold is asserted.
- Seeds are strict integers, not counts; engine-specific seed ranges remain to
  be decided. Event seeds are non-null as illustrated by the protocol; supporting
  an unavailable event seed would require a versioned change, not a fake zero.
- Metadata identifiers are nonblank strings. Execution status and event type
  use the protocol enumerations. Outcome booleans remain labels; cross-field
  scientific rules (for example timing of final success) are not invented.
- Manifest timestamps are UTC RFC3339 strings with `Z`, including optional
  fractional seconds, and are checked for calendar validity. They are strings
  to support strict JSON/YAML round trips; quote them in YAML.

Any future structural change requires a version bump and migration note per the
protocol. These contracts do not imply Stage 0 or two-trace validation is complete.

## Test-delta observation and comparability

```text
test_delta = previous comparable failing-test count - current failing-test count
```

Positive means fewer failures; negative means more failures; zero means unchanged
failure count across comparable measurements. It does not define progressing,
stagnant, regressing, recovered, or any other behavioral label.

Both measurements must use the same identified test population and execution
configuration. Account for collection/skip differences and relevant environment
changes before asserting comparability. If comparability is unknown, or either
count is unknown, `test_delta` must remain null. Do not infer zero from missing data.

Provenance needed for a future comparability review includes both measurement
references and prefix positions; collected test identities and suite/selection
version; exact commands, arguments, working directory, and runner configuration;
counts and identities of collected, executed, skipped, and deselected tests;
runner/dependency/environment versions and relevant environment changes; and
repository/patch state for each observation. Record how differences were accounted
for, the comparison decision, and its rule version. The intended code-under-test
change must be distinguishable from a changed test population or execution setup.
The reference measurement/window still needs selection and recording.

The integer contract cannot enforce this provenance or establish comparability.
These requirements are documented only; derivation and comparability checking
are not implemented. Proposed storage changes appear in
[PROTOCOL_AMENDMENTS_PROPOSED.md](PROTOCOL_AMENDMENTS_PROPOSED.md).

## Encoder input versus metadata and labels

`agentstate.schemas.projection.encoder_input(validated_record)` constructs a
separate dictionary using explicit nested field allowlists. It does not modify
the validated record or share its mutable lists or event dictionaries.

Event projections contain event details, observed environment evidence, and
resource measurements. Snapshot projections contain semantic, execution, and
resource state. Source identity, schema/bookkeeping identifiers, step IDs,
trajectory references, `outcome`, and `future_outcome` are excluded. Step IDs
are excluded as identifiers; ordered prefix construction remains a future task.
Final-type events are rejected as a temporary fail-closed restriction for
pre-terminal prediction experiments. This is not a universal prohibition on
legitimate final observations: terminal-state analysis needs a separate policy.
A direct final event prevents its whole projection, including otherwise legitimate
environment/resource evidence. A final event anywhere in `recent_events` prevents
the whole snapshot projection; it is never silently dropped. Clear errors explain
the policy, and original records remain intact. A non-final event's terminal
outcome metadata is still excluded.

Callers must establish prefix provenance BEFORE projection: every retained value
must have been observed at the chosen cutoff, and summaries must use only that
prefix. The contract cannot prove temporal provenance. In particular, filtering
fields does not remove identity clues or future labels embedded in semantic
text, summaries, paths, tool names, or error strings. Tool names and paths retain
legitimate observed evidence but require later normalization and leakage audits.
The projection is not a guarantee of invariance or leakage elimination.
Free-text filtering or keyword removal cannot prove absence of leakage. Outcome
information can remain in summaries, semantic content (including non-final nested
`recent_events`), patch summaries, and error messages. No automatic text sanitizer
is implemented or implied.

## Draft versus run-ready manifest

The YAML manifest identifies the first Qwen3-4B-Instruct-2507 + AutoGen experiment
on one SWE-bench Lite task. Its experiment ID is a local configuration name, not
an invented task/run result. Versions `0.1-draft` and `0.1` identify this draft
configuration/contract and the protocol, respectively.

All unresolved revisions, software versions, instance ID, prompt version,
sampling parameters, context, tools, budgets, Git commit, hardware, evaluator,
and timestamps are explicit nulls. Model quantization and license are also
recorded because the protocol requires them to be frozen. The checkpoint name
comes from the protocol; registry URI and exact revision still need verification.

`ExperimentManifest.model_validate(...)` accepts structurally valid drafts with
explicit nulls, but rejects a manifest marked `status: run_ready` if required
configuration values are unresolved. An after-validator calls the same
`manifest.assert_run_ready()` implementation used by explicit readiness checks
and the CLI. That method requires `status: run_ready` and all required
configuration fields resolved. Setting the status alone cannot pass validation.
It checks nested values and reports unresolved paths. A seed may remain null
only if `seed_controllable` is explicitly false. `started_at` and `ended_at` may
remain null before execution; `created_at` must be known. These exemptions allow
pre-execution readiness without fabricating future actual timestamps.

Known absence must be explicit (for example `quantization: none`, an empty tools
list for an intentionally tool-free setup, or zero accelerator memory for CPU
execution), and must match the selected configuration. String placeholders such
as `TBD`, `TODO`, `unknown`, and `unresolved` also fail readiness; use null. Completeness
checking cannot establish that a non-null revision/version is real or that a
selected budget is scientifically appropriate. Run readiness here is a
configuration-completeness check, not authorization, feasibility, or successful
experimental validation. Verify values and record review decisions separately.
Generated JSON Schemas express structural validation; the Python after-validator
is not exported as JSON Schema conditional readiness rules. Use Pydantic or the
CLI to enforce run-ready completeness, not JSON Schema validation alone.

Raw/normalized trace locations and terminal outcome belong to future run
records; this manifest is a pre-run configuration. The protocol's full run
provenance requirements remain to be implemented with collectors and artifact
storage. They are not claimed complete by this draft.

## Unresolved scientific decisions and next step

No thresholds or labeling logic are defined for progressing, stagnant,
regressing, recovered, looping, recovery, or semantic equivalence. Operational
definitions, ambiguity handling, annotation versions, and reliability checks
remain necessary. Pair construction, repeated-action scoring, test-measurement
comparability rules and reference selection, prefix windows, normalization strength,
and numerical experiment
gates remain unresolved. Preserve the existing task/repository-aware evaluation
and all leakage controls while resolving these questions.

The next recommended step is to review these provisional interpretations and
resolve the first experiment's manifest with verified values and explicit
budget/tool decisions. Then separately authorize AutoGen raw-trace collection
for one task, followed by the same task in LangGraph and two-trace validation.
Do not scale before the protocol gate is satisfied.

[PROTOCOL_AMENDMENTS_PROPOSED.md](PROTOCOL_AMENDMENTS_PROPOSED.md) records
unadopted proposals; no event/snapshot field structure or nullability is changed.
