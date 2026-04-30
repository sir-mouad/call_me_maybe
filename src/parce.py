import sys
import argparse
import json
from pydantic import BaseModel, Field, ValidationError, ConfigDict


class RequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1)


class TypeInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1)


class FunctionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, TypeInfo]
    returns: TypeInfo


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def check_parce_input(data: list[dict]) -> list[str]:
    prompts = []
    for item in data:
        validated = RequestInput.model_validate(item)
        prompts.append(validated.prompt)

    return prompts

    
def check_parce_diff(data: list[dict]) -> list[FunctionDefinition]:
    functions = []

    for item in data:
        validated = FunctionDefinition.model_validate(item)
        functions.append(validated)

    return functions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition", default="data/input/functions_definition.json")
    parser.add_argument("--input", default="data/input/function_calling_tests.json")
    parser.add_argument("--output", default="data/output/function_calling_results.json")
    args = parser.parse_args()

    try:
        data_input = load_json(args.input)
        data_diff = load_json(args.functions_definition)

        prompts = check_parce_input(data_input)
        functions = check_parce_diff(data_diff)

        print(prompts)
        print(functions)

    except FileNotFoundError as error:
        print(f"file not found: {error}")
        sys.exit(1)

    except json.JSONDecodeError as error:
        print(f"invalid json: {error}")
        sys.exit(1)

    except ValidationError as error:
        for e in error.errors():
            print(e["msg"])
        sys.exit(1)

if __name__ == "__main__":
    main()
