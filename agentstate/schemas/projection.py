"""Allowlisted prefix data. This does not sanitize identity or future labels in text."""

from .contracts import AgentEvent, EventDetails, StateSnapshot


def _event(event: EventDetails) -> dict:
    if event.event_type == "final":
        raise ValueError(
            "Final events are temporarily ineligible for pre-terminal prediction projection; "
            "terminal-state analysis needs a separate policy. No events are silently dropped; "
            "the original record remains intact."
        )
    return {
        "event_type": event.event_type,
        "semantic_content": event.semantic_content,
        "tool_family": event.tool_family,
        "tool_name": event.tool_name,
        "execution_status": event.execution_status,
    }


def encoder_input(record: AgentEvent | StateSnapshot) -> dict:
    """Return a separate object after the caller establishes prefix provenance.

    This temporary pre-terminal policy rejects final events, including nested ones.
    Field filtering or keyword removal cannot prove absence of free-text leakage.
    """
    if isinstance(record, AgentEvent):
        environment = record.environment
        resources = record.resources
        return {
            "event": _event(record.event),
            "environment": {
                "files_inspected": list(environment.files_inspected),
                "files_modified": list(environment.files_modified),
                "tests_passed": environment.tests_passed,
                "tests_failed": environment.tests_failed,
                "new_failures": environment.new_failures,
                "resolved_failures": environment.resolved_failures,
                "error_signatures": list(environment.error_signatures),
                "patch_summary": environment.patch_summary,
            },
            "resources": {
                "input_tokens": resources.input_tokens,
                "output_tokens": resources.output_tokens,
                "cumulative_tokens": resources.cumulative_tokens,
                "tool_calls": resources.tool_calls,
                "elapsed_ms": resources.elapsed_ms,
            },
        }
    if not isinstance(record, StateSnapshot):
        raise TypeError("Expected a validated AgentEvent or StateSnapshot")
    execution = record.execution_state
    resources = record.resource_state
    return {
        "semantic_state": {
            "recent_events": [_event(event) for event in record.semantic_state.recent_events],
            "agent_summary": record.semantic_state.agent_summary,
        },
        "execution_state": {
            "files_inspected_count": execution.files_inspected_count,
            "files_modified_count": execution.files_modified_count,
            "tests_passed": execution.tests_passed,
            "tests_failed": execution.tests_failed,
            "test_delta": execution.test_delta,
            "tool_successes": execution.tool_successes,
            "tool_failures": execution.tool_failures,
            "repeated_action_score": execution.repeated_action_score,
            "active_error_signatures": list(execution.active_error_signatures),
        },
        "resource_state": {
            "cumulative_input_tokens": resources.cumulative_input_tokens,
            "cumulative_output_tokens": resources.cumulative_output_tokens,
            "cumulative_tool_calls": resources.cumulative_tool_calls,
            "elapsed_ms": resources.elapsed_ms,
        },
    }
