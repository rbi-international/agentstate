"""Strict data contracts; scientific interpretations are in docs/DATA_CONTRACTS.md."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Count = Annotated[int, Field(ge=0)]
Text = Annotated[str, Field(min_length=1, pattern=r"\S")]
Score = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Timestamp = Annotated[
    str,
    Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$",
        json_schema_extra={"format": "date-time"},
    ),
]


class Contract(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


class Source(Contract):
    model_id: Text
    model_revision: Text
    framework_id: Text
    framework_version: Text
    run_id: Text
    seed: int


class EventDetails(Contract):
    event_type: Literal[
        "reasoning", "action", "tool_call", "observation", "environment_change", "final"
    ]
    semantic_content: str | None
    tool_family: str | None
    tool_name: str | None
    execution_status: Literal["success", "failure", "partial", "unknown"]


class Environment(Contract):
    files_inspected: list[str]
    files_modified: list[str]
    tests_passed: Count | None
    tests_failed: Count | None
    new_failures: Count | None
    resolved_failures: Count | None
    error_signatures: list[str]
    patch_summary: str | None


class Resources(Contract):
    input_tokens: Count | None
    output_tokens: Count | None
    cumulative_tokens: Count | None
    tool_calls: Count | None
    elapsed_ms: Count | None


class Outcome(Contract):
    terminal: bool
    final_success: bool | None


class AgentEvent(Contract):
    schema_version: Literal["0.1"]
    trajectory_id: Text
    task_id: Text
    step_id: Count
    source: Source
    event: EventDetails
    environment: Environment
    resources: Resources
    outcome: Outcome


class SemanticState(Contract):
    recent_events: list[EventDetails]
    agent_summary: str | None


class ExecutionState(Contract):
    files_inspected_count: Count
    files_modified_count: Count
    tests_passed: Count | None
    tests_failed: Count | None
    test_delta: int | None = Field(
        description=(
            "Previous comparable failing-test count minus current failing-test count. "
            "Positive means fewer failures; negative means more failures. Observation, "
            "not a behavioral label. Must be null when comparability is unknown; "
            "the integer contract does not enforce measurement provenance."
        )
    )
    tool_successes: Count
    tool_failures: Count
    repeated_action_score: Score | None
    active_error_signatures: list[str]


class ResourceState(Contract):
    cumulative_input_tokens: Count | None
    cumulative_output_tokens: Count | None
    cumulative_tool_calls: Count
    elapsed_ms: Count | None


class FutureOutcome(Contract):
    eventual_success: bool | None
    steps_to_terminal: Count | None
    tokens_to_terminal: Count | None
    future_recovery_observed: bool | None


class StateSnapshot(Contract):
    state_id: Text
    trajectory_id: Text
    task_id: Text
    step: Count
    trajectory_prefix_ref: Text
    semantic_state: SemanticState
    execution_state: ExecutionState
    resource_state: ResourceState
    future_outcome: FutureOutcome


class ModelSpec(Contract):
    checkpoint: Text
    revision: Text | None
    quantization: Text | None
    license: Text | None


class SoftwareSpec(Contract):
    name: Text | None
    version: Text | None


class TaskSpec(Contract):
    benchmark: Text
    dataset_revision: Text | None
    instance_id: Text | None


class Sampling(Contract):
    temperature: Annotated[float, Field(ge=0)] | None
    top_p: Annotated[float, Field(gt=0, le=1)] | None
    top_k: Count | None
    seed: int | None
    seed_controllable: bool | None


class ToolSpec(Contract):
    name: Text
    version: Text
    configuration: Text


class Budgets(Contract):
    timeout_seconds: Count | None
    max_steps: Count | None
    max_tool_calls: Count | None
    max_input_tokens: Count | None
    max_output_tokens: Count | None


class Hardware(Contract):
    os: Text | None
    cpu: Text | None
    ram_bytes: Count | None
    accelerator: Text | None
    accelerator_memory_bytes: Count | None


class Timestamps(Contract):
    created_at: Timestamp | None
    started_at: Timestamp | None
    ended_at: Timestamp | None

    @field_validator("created_at", "started_at", "ended_at")
    @classmethod
    def valid_calendar_time(cls, value: str | None) -> str | None:
        if value is not None:
            datetime.fromisoformat(value)
        return value


class ExperimentManifest(Contract):
    manifest_version: Literal["0.1"]
    experiment_id: Text
    experiment_version: Text
    protocol_version: Literal["0.1"]
    status: Literal["draft", "run_ready"]
    model: ModelSpec
    framework: SoftwareSpec
    inference_engine: SoftwareSpec
    task: TaskSpec
    prompt_template_version: Text | None
    sampling: Sampling
    context_limit: Count | None
    tools: list[ToolSpec] | None
    budgets: Budgets
    git_commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")] | None
    hardware: Hardware
    evaluator: SoftwareSpec
    timestamps: Timestamps

    @model_validator(mode="after")
    def validate_run_ready_status(self) -> Self:
        if self.status == "run_ready":
            self.assert_run_ready()
        return self

    def assert_run_ready(self) -> None:
        """Check configuration completeness, without starting or authorizing a run."""
        exempt = {"timestamps.started_at", "timestamps.ended_at"}
        if self.sampling.seed_controllable is False:
            exempt.add("sampling.seed")
        unresolved: list[str] = []

        def visit(value: object, path: str) -> None:
            if (
                value is None
                and path not in exempt
                or isinstance(value, str)
                and value.strip().casefold()
                in {
                    "tbd",
                    "todo",
                    "unknown",
                    "unresolved",
                    "<unresolved>",
                }
            ):
                unresolved.append(path)
            elif isinstance(value, dict):
                for key, item in value.items():
                    visit(item, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    visit(item, f"{path}[{index}]")

        visit(self.model_dump(), "")
        if self.status != "run_ready":
            unresolved.insert(0, "status (must be run_ready)")
        if unresolved:
            raise ValueError("Manifest is not run-ready: " + ", ".join(unresolved))
