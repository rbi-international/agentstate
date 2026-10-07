"""Generate JSON Schemas from Pydantic contracts: python -m agentstate.schemas.generate."""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from . import AgentEvent, ExperimentManifest, StateSnapshot


def generate(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for contract in (AgentEvent, StateSnapshot, ExperimentManifest):
        schema = contract.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)
        (output / f"{contract.__name__}.schema.json").write_text(
            json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("agentstate/schemas/json"))
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()
