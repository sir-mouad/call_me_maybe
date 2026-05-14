import sys
import argparse
import json
from typing import Any
from pydantic import BaseModel, Field, ValidationError, ConfigDict, model_validator, field_validator


class RequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1)


SUPPORTED_TYPES = {"number", "string", "boolean"}


class FunctionDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, str]
    returns: str

    @field_validator("parameters")
    @classmethod
    def check_types(cls, params):
        for name, t in params.items():
            if t not in SUPPORTED_TYPES:
                raise ValueError(
                    f"unsupported type '{t}' for parameter '{name}'")
        return params

    @model_validator(mode="before")
    @classmethod
    def flatten(cls, data: Any) -> Any:
        """Flatten {"a": {"type": "number"}} -> {"a": "number"}."""
        if isinstance(data.get("parameters"), dict):
            data["parameters"] = {
                k: v["type"] for k, v in data["parameters"].items()
            }
        if isinstance(data.get("returns"), dict):
            data["returns"] = data["returns"]["type"]
        return data


def load_json(path: str) -> Any:
    """Load and return parsed JSON from a file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_prompts(data: Any) -> list[str]:
    """Validate and extract prompts from raw JSON data.

    Args:
        data: Raw parsed JSON input.

    Returns:
        List of validated prompt strings.

    Raises:
        ValueError: If data is not a list.
    """
    if not isinstance(data, list):
        raise ValueError("input file must be a JSON array")
    return [RequestInput.model_validate(item).prompt for item in data]


def parse_functions(data: Any) -> list[FunctionDefinition]:
    """Validate and extract function definitions from raw JSON data.

    Args:
        data: Raw parsed JSON input.

    Returns:
        List of validated FunctionDefinition objects.

    Raises:
        ValueError: If data is not a list.
    """
    if not isinstance(data, list):
        raise ValueError("functions definition file must be a JSON array")
    return [FunctionDefinition.model_validate(item) for item in data]


def get_and_check_inputs() -> tuple[list[str], list[FunctionDefinition], str]:
    """Parse CLI args, load and validate input files.

    Returns:
        A tuple of (prompts, functions, output_path).
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json"
    )
    arg_parser.add_argument(
        "--input", default="data/input/function_calling_tests.json")
    arg_parser.add_argument(
        "--output", default="data/output/function_calling_results.json")
    args = arg_parser.parse_args()

    try:
        prompts = parse_prompts(load_json(args.input))
        functions = parse_functions(load_json(args.functions_definition))
        return prompts, functions, args.output
    except FileNotFoundError as error:
        print(f"file not found: {error}")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"invalid json: {error}")
        sys.exit(1)
    except ValueError as error:
        print(f"error: {error}")
        sys.exit(1)
    except ValidationError as error:
        for e in error.errors():
            loc = " -> ".join(str(l) for l in e["loc"])
            print(f"validation error at {loc}: {e['msg']}")
        sys.exit(1)


if __name__ == "__main__":
    get_and_check_inputs()
