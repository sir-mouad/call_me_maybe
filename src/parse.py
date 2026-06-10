import sys
import argparse
import json
from typing import Any
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    model_validator,
    field_validator
)


class RequestInput(BaseModel):
    """Pydantic model for validating a single input prompt."""

    prompt: str = Field(min_length=1)


SUPPORTED_TYPES: set[str] = {"number", "string", "boolean", "integer"}


class FunctionDefinition(BaseModel):
    """Pydantic model for validating a function definition."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, str]
    returns: str

    @field_validator("parameters")
    @classmethod
    def check_types(cls, params: dict[str, str]) -> dict[str, str]:
        """Validate that all parameter types are supported.

        Args:
            params: Dict of parameter names to their types.

        Returns:
            The validated parameters dict.

        Raises:
            ValueError: If an unsupported type is found.
        """
        for name, t in params.items():
            if t not in SUPPORTED_TYPES:
                raise ValueError(
                    f"unsupported type '{t}' for parameter '{name}'")
        return params

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, data: Any) -> Any:
        """normalize nested type dicts into plain strings.

        Args:
            data: Raw input data before validation.

        Returns:
            normalizeed data with string types.
        """
        if isinstance(data.get("parameters"), dict):
            parameters = {}
            for k, v in data["parameters"].items():
                parameters[k] = v["type"]

            data["parameters"] = parameters
        if isinstance(data.get("returns"), dict):
            data["returns"] = data["returns"]["type"]
        return data


def load_json(path: str) -> list:
    """Load and return parsed JSON from a file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_prompts(data: list) -> list[str]:
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
    result = []
    for item in data:
        obj = RequestInput.model_validate(item)
        result.append(obj.prompt)

    return result



def parse_functions(data: list) -> list[FunctionDefinition]:
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
    result = []
    for item in data:
        result.append(FunctionDefinition.model_validate(item))

    return result


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
        "--output", default="data/output/function_calls.json")
    args = arg_parser.parse_args()

    try:
        prompts = parse_prompts(load_json(args.input))
        functions = parse_functions(load_json(args.functions_definition))
        return prompts, functions, args.output
    except FileNotFoundError as error:
        print(f"error: file not found: {error.filename}")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"error: invalid json: {error.msg}")
        sys.exit(1)
    except ValueError as error:
        print(f"error: {error}")
        sys.exit(1)
    except ValidationError as error:
        for e in error.errors():
            print(f"error: {e['msg']}")
        sys.exit(1)


if __name__ == "__main__":
    get_and_check_inputs()
