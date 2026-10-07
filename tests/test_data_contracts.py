"""All records in this module are SYNTHETIC fixtures, not experimental evidence."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from agentstate.schemas import AgentEvent, ExperimentManifest, StateSnapshot
from agentstate.schemas.generate import generate
from agentstate.schemas.projection import encoder_input

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def event():
    """Synthetic prefix observation."""
    return {
        "schema_version": "0.1",
        "trajectory_id": "synthetic-trace",
        "task_id": "synthetic-task",
        "step_id": 0,
        "source": {
            "model_id": "synthetic-model",
            "model_revision": "synthetic-revision",
            "framework_id": "synthetic-framework",
            "framework_version": "synthetic-version",
            "run_id": "synthetic-run",
            "seed": 0,
        },
        "event": {
            "event_type": "observation",
            "semantic_content": "Synthetic test observation",
            "tool_family": "tests",
            "tool_name": "synthetic-tool",
            "execution_status": "unknown",
        },
        "environment": {
            "files_inspected": ["synthetic.py"],
            "files_modified": [],
            "tests_passed": None,
            "tests_failed": None,
            "new_failures": None,
            "resolved_failures": None,
            "error_signatures": [],
            "patch_summary": None,
        },
        "resources": dict.fromkeys(
            ["input_tokens", "output_tokens", "cumulative_tokens", "tool_calls", "elapsed_ms"]
        ),
        "outcome": {"terminal": False, "final_success": None},
    }


@pytest.fixture
def snapshot(event):
    """Synthetic snapshot; future labels deliberately populated to test exclusion."""
    return {
        "state_id": "synthetic-state",
        "trajectory_id": "synthetic-trace",
        "task_id": "synthetic-task",
        "step": 0,
        "trajectory_prefix_ref": "synthetic://prefix-only",
        "semantic_state": {"recent_events": [event["event"]], "agent_summary": None},
        "execution_state": {
            "files_inspected_count": 0,
            "files_modified_count": 0,
            "tests_passed": None,
            "tests_failed": None,
            "test_delta": -2,
            "tool_successes": 0,
            "tool_failures": 0,
            "repeated_action_score": None,
            "active_error_signatures": [],
        },
        "resource_state": {
            "cumulative_input_tokens": None,
            "cumulative_output_tokens": None,
            "cumulative_tool_calls": 0,
            "elapsed_ms": None,
        },
        "future_outcome": {
            "eventual_success": True,
            "steps_to_terminal": 2,
            "tokens_to_terminal": 100,
            "future_recovery_observed": False,
        },
    }


def draft():
    return yaml.safe_load(
        (ROOT / "configs/experiments/qwen_autogen_trace_validation.yaml").read_text()
    )


def test_valid_records_and_nulls(event, snapshot):
    assert AgentEvent.model_validate(event).model_dump() == event
    assert StateSnapshot.model_validate(snapshot).model_dump() == snapshot
    assert encoder_input(AgentEvent.model_validate(event))["resources"]["input_tokens"] is None
    assert (
        encoder_input(StateSnapshot.model_validate(snapshot))["execution_state"]["tests_passed"]
        is None
    )


@pytest.mark.parametrize(
    "section,field",
    [
        (None, "step_id"),
        ("environment", "tests_passed"),
        ("environment", "tests_failed"),
        ("environment", "new_failures"),
        ("environment", "resolved_failures"),
        *[
            ("resources", key)
            for key in (
                "input_tokens",
                "output_tokens",
                "cumulative_tokens",
                "tool_calls",
                "elapsed_ms",
            )
        ],
    ],
)
def test_negative_event_counts(event, section, field):
    (event[section] if section else event)[field] = -1
    with pytest.raises(ValidationError):
        AgentEvent.model_validate(event)


@pytest.mark.parametrize(
    "section,field",
    [
        (None, "step"),
        *[
            ("execution_state", key)
            for key in (
                "files_inspected_count",
                "files_modified_count",
                "tests_passed",
                "tests_failed",
                "tool_successes",
                "tool_failures",
                "repeated_action_score",
            )
        ],
        *[
            ("resource_state", key)
            for key in (
                "cumulative_input_tokens",
                "cumulative_output_tokens",
                "cumulative_tool_calls",
                "elapsed_ms",
            )
        ],
        ("future_outcome", "steps_to_terminal"),
        ("future_outcome", "tokens_to_terminal"),
    ],
)
def test_negative_snapshot_counts(snapshot, section, field):
    (snapshot[section] if section else snapshot)[field] = -1
    with pytest.raises(ValidationError):
        StateSnapshot.model_validate(snapshot)


@pytest.mark.parametrize(
    "section", [None, "source", "event", "environment", "resources", "outcome"]
)
def test_extra_event_fields(event, section):
    (event[section] if section else event)["unexpected"] = "synthetic"
    with pytest.raises(ValidationError):
        AgentEvent.model_validate(event)


@pytest.mark.parametrize(
    "section", [None, "semantic_state", "execution_state", "resource_state", "future_outcome"]
)
def test_extra_snapshot_fields(snapshot, section):
    (snapshot[section] if section else snapshot)["unexpected"] = "synthetic"
    with pytest.raises(ValidationError):
        StateSnapshot.model_validate(snapshot)


@pytest.mark.parametrize("value", ["0", 0.5, True])
def test_strict_integer(event, value):
    event["step_id"] = value
    with pytest.raises(ValidationError):
        AgentEvent.model_validate(event)


@pytest.mark.parametrize("field", ["event_type", "execution_status"])
def test_invalid_enums(event, field):
    event["event"][field] = "invalid"
    with pytest.raises(ValidationError):
        AgentEvent.model_validate(event)


def test_draft_not_run_ready():
    data = draft()
    manifest = ExperimentManifest.model_validate(data)
    with pytest.raises(ValueError, match="model.revision"):
        manifest.assert_run_ready()
    data["status"] = "run_ready"
    with pytest.raises(ValidationError, match="model.revision"):
        ExperimentManifest.model_validate(data)


@pytest.mark.parametrize("sentinel", ["TBD", "TODO", "unknown", "unresolved"])
def test_readiness_rejects_string_placeholders(sentinel):
    data = draft()
    data["status"] = "run_ready"
    data["model"]["revision"] = sentinel
    with pytest.raises(ValidationError, match="model.revision"):
        ExperimentManifest.model_validate(data)


@pytest.fixture
def ready_configuration():
    """Synthetic resolved configuration, not verified hardware or experiment settings."""
    data = draft()

    def resolve(value):
        if isinstance(value, dict):
            return {k: resolve(v) for k, v in value.items()}
        return "synthetic" if value is None else value

    data = resolve(data)
    data.update(status="run_ready", context_limit=1, git_commit="a" * 40, tools=[])
    data["sampling"] = {
        "temperature": 0.0,
        "top_p": 1.0,
        "top_k": 0,
        "seed": None,
        "seed_controllable": False,
    }
    data["budgets"] = dict.fromkeys(data["budgets"], 1)
    data["hardware"].update(ram_bytes=1, accelerator_memory_bytes=0)
    data["timestamps"] = {
        "created_at": "2026-10-02T00:00:00Z",
        "started_at": None,
        "ended_at": None,
    }
    return data


def test_synthetic_complete_configuration(ready_configuration):
    manifest = ExperimentManifest.model_validate(ready_configuration)
    manifest.assert_run_ready()
    assert manifest.timestamps.started_at is None
    assert manifest.timestamps.ended_at is None
    assert manifest.sampling.seed is None


@pytest.mark.parametrize("controllable,seed", [(False, None), (True, 0), (True, 23)])
def test_readiness_seed_exemptions(ready_configuration, controllable, seed):
    ready_configuration["sampling"].update(seed_controllable=controllable, seed=seed)
    ExperimentManifest.model_validate(ready_configuration).assert_run_ready()


@pytest.mark.parametrize("controllable", [True, None])
def test_unresolved_controllable_seed_rejected(ready_configuration, controllable):
    ready_configuration["sampling"]["seed_controllable"] = controllable
    with pytest.raises(ValidationError, match="sampling.seed"):
        ExperimentManifest.model_validate(ready_configuration)


@pytest.mark.parametrize(
    "path",
    [
        ("model", "revision"),
        ("framework", "version"),
        ("task", "instance_id"),
        ("sampling", "temperature"),
        ("budgets", "max_steps"),
        ("timestamps", "created_at"),
        ("tools",),
        ("context_limit",),
    ],
)
def test_single_unresolved_required_value_rejected(ready_configuration, path):
    target = ready_configuration
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = None
    before = deepcopy(ready_configuration)
    with pytest.raises(ValidationError, match="\\.".join(path)):
        ExperimentManifest.model_validate(ready_configuration)
    assert ready_configuration == before
    ready_configuration["status"] = "draft"
    draft_manifest = ExperimentManifest.model_validate(ready_configuration)
    with pytest.raises(ValueError, match="\\.".join(path)):
        draft_manifest.assert_run_ready()


def test_nested_tool_completeness(ready_configuration):
    ready_configuration["tools"] = [
        {"name": "synthetic-tool", "version": "TBD", "configuration": "synthetic"}
    ]
    with pytest.raises(ValidationError, match=r"tools\[0\].version"):
        ExperimentManifest.model_validate(ready_configuration)


@pytest.mark.parametrize(
    "fixture,contract,keys",
    [
        ("event", AgentEvent, {"event", "environment", "resources"}),
        ("snapshot", StateSnapshot, {"semantic_state", "execution_state", "resource_state"}),
    ],
)
def test_projection_is_separate_allowlisted_object(request, fixture, contract, keys):
    record = contract.model_validate(request.getfixturevalue(fixture))
    before = deepcopy(record.model_dump())
    projected = encoder_input(record)
    assert set(projected) == keys
    serialized = json.dumps(projected)
    for forbidden in (
        "source",
        "model_id",
        "framework_id",
        "task_id",
        "trajectory_id",
        "step_id",
        "state_id",
        "trajectory_prefix_ref",
        "future_outcome",
        "final_success",
        "eventual_success",
        "steps_to_terminal",
        "terminal",
    ):
        assert f'"{forbidden}"' not in serialized
    if fixture == "event":
        projected["environment"]["files_inspected"].append("changed")
    else:
        projected["semantic_state"]["recent_events"][0]["semantic_content"] = "changed"
        projected["execution_state"]["active_error_signatures"].append("changed")
    assert record.model_dump() == before


@pytest.mark.parametrize("kind", ["direct", "nested"])
def test_final_events_require_separate_policy(event, snapshot, kind):
    if kind == "direct":
        event["event"]["event_type"] = "final"
        record = AgentEvent.model_validate(event)
    else:
        # Keep a legitimate observation before the final detail; do not silently drop either.
        snapshot["semantic_state"]["recent_events"].append(
            {**deepcopy(event["event"]), "event_type": "final"}
        )
        record = StateSnapshot.model_validate(snapshot)
    before = deepcopy(record.model_dump())
    with pytest.raises(ValueError, match="pre-terminal prediction") as error:
        encoder_input(record)
    assert "terminal-state analysis needs a separate policy" in str(error.value)
    assert "No events are silently dropped" in str(error.value)
    assert record.model_dump() == before


def test_generated_schemas_and_representative_records(tmp_path, event, snapshot):
    generate(tmp_path)
    for contract, record in (
        (AgentEvent, event),
        (StateSnapshot, snapshot),
        (ExperimentManifest, draft()),
    ):
        filename = f"{contract.__name__}.schema.json"
        schema = json.loads((tmp_path / filename).read_text())
        assert (tmp_path / filename).read_bytes() == (
            ROOT / "agentstate/schemas/json" / filename
        ).read_bytes()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        validator.validate(record)
        invalid = deepcopy(record)
        invalid["unexpected"] = True
        assert list(validator.iter_errors(invalid))


def test_invalid_timestamp_and_manifest_fields():
    data = draft()
    data["timestamps"]["created_at"] = "2026-02-30T00:00:00Z"
    with pytest.raises(ValidationError):
        ExperimentManifest.model_validate(data)
    data = draft()
    data["budgets"]["max_steps"] = -1
    with pytest.raises(ValidationError):
        ExperimentManifest.model_validate(data)
    data = draft()
    data["model"]["unexpected"] = True
    with pytest.raises(ValidationError):
        ExperimentManifest.model_validate(data)
