import sys
import argparse
import json
from typing import Any
from pydantic import BaseModel, Field, ValidationError, ConfigDict


class RequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1)


class TypeInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str = Field(min_length=1)


class FunctionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, TypeInfo]
    returns: TypeInfo


def load_json(path: str) -> Any:
    """Load and return parsed JSON from a file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_parse_input(data: Any) -> list[str]:
    """Validate and extract prompts from input data.

    Args:
        data: Raw parsed JSON input.

    Returns:
        List of validated prompt strings.
    """
    if not isinstance(data, list):
        print("error: input file must be a JSON array")
        sys.exit(1)
    prompts = []
    for item in data:
        validated = RequestInput.model_validate(item)
        prompts.append(validated.prompt)
    return prompts


def check_parse_functions(data: Any) -> list[FunctionDefinition]:
    """Validate and extract function definitions from input data.

    Args:
        data: Raw parsed JSON input.

    Returns:
        List of validated FunctionDefinition objects.
    """
    if not isinstance(data, list):
        print("error: functions definition file must be a JSON array")
        sys.exit(1)
    functions = []
    for item in data:
        validated = FunctionDefinition.model_validate(item)
        functions.append(validated)
    return functions  

def get_and_check_inputs() -> None:
    """Entry point for the function calling tool."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json"
    )
    parser.add_argument("--input", default="data/input/function_calling_tests.json")
    parser.add_argument("--output", default="data/output/function_calling_results.json")
    args = parser.parse_args()

    try:
        data_input = load_json(args.input)
        data_diff = load_json(args.functions_definition)
        prompts = check_parse_input(data_input)
        functions = check_parse_functions(data_diff)
        return prompts, functions
    except FileNotFoundError as error:
        print(f"file not found: {error}")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"invalid json: {error}")
        sys.exit(1)
    except ValidationError as error:
        for e in error.errors():
            print(f"validation error at {e['loc']}: {e['msg']}")
        sys.exit(1)


if __name__ == "__main__":
    get_and_check_inputs()