import sys
import argparse
import json
from pydantic import ValidationError
from src.pydantic_model import RequestInput, FunctionDefinition


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
        "--output", default="data/output/function_calling_results.json")
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
        print(f"error: {error.errors()[0]["msg"]} in "
              f"{error.errors()[0]["input"]}")
        sys.exit(1)
    except ValidationError as error:
        print(f"error: {error.errors()[0]["msg"]} in "
              f"{error.errors()[0]["input"]}")
        sys.exit(1)
