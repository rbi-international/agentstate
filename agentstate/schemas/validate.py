"""Validate JSON records or a YAML manifest without executing any experiment."""

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from . import AgentEvent, ExperimentManifest, StateSnapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["event", "snapshot", "manifest"])
    parser.add_argument("path", type=Path)
    parser.add_argument("--run-ready", action="store_true")
    args = parser.parse_args()
    if args.run_ready and args.kind != "manifest":
        parser.error("--run-ready applies only to manifests")
    text = args.path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if args.kind == "manifest" else json.loads(text)
    contract = {"event": AgentEvent, "snapshot": StateSnapshot, "manifest": ExperimentManifest}[
        args.kind
    ]
    try:
        record = contract.model_validate(data)
        schema = contract.model_json_schema()
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
        if args.run_ready:
            record.assert_run_ready()
    except (ValueError, TypeError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
    print(f"Valid {args.kind}" + ("; run-readiness check passed" if args.run_ready else ""))


if __name__ == "__main__":
    main()
